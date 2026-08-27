import io
import re
import time
import wave

import numpy as np
from groq import Groq
from scipy.signal import resample_poly

from backend.config import groq_api_key

def clean_text_for_tts(text: str) -> str:

    # Remove bold markdown
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    # Remove italic markdown
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"\1",
        text
    )

    # Remove inline code
    text = re.sub(
        r"`([^`]*)`",
        r"\1",
        text
    )

    # Remove markdown links but keep visible text
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove markdown headings
    text = re.sub(
        r"^\s*#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    return text.strip()

class GroqTTS:

    def __init__(
        self,
        model="canopylabs/orpheus-v1-english",
        voice="hannah",
    ):
        print("Initializing Groq TTS...")

        self.client = Groq(
            api_key=groq_api_key
        )

        self.model = model
        self.voice = voice

        print("Groq TTS initialized.")

    # ==================================================
    # SPLIT TEXT INTO TTS-SAFE CHUNKS
    # ==================================================

    def split_text(
        self,
        text: str,
        max_chars: int = 180
    ):

        text = text.strip()

        if not text:
            return []

        # ----------------------------------------------
        # FIRST SPLIT AT SENTENCE BOUNDARIES
        # ----------------------------------------------

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        chunks = []
        current = ""

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            # ------------------------------------------
            # SENTENCE FITS WITHIN LIMIT
            # ------------------------------------------

            if len(sentence) <= max_chars:

                if current:

                    candidate = (
                        current
                        + " "
                        + sentence
                    )

                else:

                    candidate = sentence

                if len(candidate) <= max_chars:

                    current = candidate

                else:

                    if current:
                        chunks.append(current)

                    current = sentence

            # ------------------------------------------
            # SENTENCE ITSELF IS TOO LONG
            # ------------------------------------------

            else:

                if current:

                    chunks.append(
                        current
                    )

                    current = ""

                words = sentence.split()

                word_chunk = ""

                for word in words:

                    if word_chunk:

                        candidate = (
                            word_chunk
                            + " "
                            + word
                        )

                    else:

                        candidate = word

                    if len(candidate) <= max_chars:

                        word_chunk = candidate

                    else:

                        if word_chunk:

                            chunks.append(
                                word_chunk
                            )

                        word_chunk = word

                if word_chunk:

                    current = word_chunk

        if current:

            chunks.append(
                current
            )

        return chunks

    # ==================================================
    # GENERATE ONE TTS CHUNK
    # ==================================================

    def _generate_chunk(
        self,
        text: str
    ):

        print(
            f"Generating Groq TTS chunk "
            f"({len(text)} characters)"
        )

        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            response_format="wav",
            speed=1.4,

        )

        wav_bytes = response.read()

        # ----------------------------------------------
        # READ WAV
        # ----------------------------------------------

        wav_buffer = io.BytesIO(
            wav_bytes
        )

        with wave.open(
            wav_buffer,
            "rb"
        ) as wav_file:

            sample_rate = (
                wav_file.getframerate()
            )

            channels = (
                wav_file.getnchannels()
            )

            sample_width = (
                wav_file.getsampwidth()
            )

            raw_audio = wav_file.readframes(
                wav_file.getnframes()
            )

        print(
            f"Chunk audio: "
            f"{sample_rate} Hz, "
            f"{channels} channel(s), "
            f"{sample_width * 8}-bit"
        )

        # ----------------------------------------------
        # WAV → FLOAT32
        # ----------------------------------------------

        if sample_width == 2:

            audio = np.frombuffer(
                raw_audio,
                dtype=np.int16
            ).astype(
                np.float32
            )

            audio /= 32768.0

        elif sample_width == 4:

            audio = np.frombuffer(
                raw_audio,
                dtype=np.int32
            ).astype(
                np.float32
            )

            audio /= 2147483648.0

        else:

            raise ValueError(
                f"Unsupported WAV sample width: "
                f"{sample_width} bytes"
            )

        # ----------------------------------------------
        # CONVERT TO MONO
        # ----------------------------------------------

        if channels > 1:

            audio = audio.reshape(
                -1,
                channels
            )

            audio = audio.mean(
                axis=1
            )

        # ----------------------------------------------
        # RESAMPLE TO 16 kHz
        # ----------------------------------------------

        target_sample_rate = 16000

        if sample_rate != target_sample_rate:

            audio = resample_poly(
                audio,
                target_sample_rate,
                sample_rate
            )

        # ----------------------------------------------
        # FLOAT32
        # ----------------------------------------------

        audio = np.asarray(
            audio,
            dtype=np.float32
        )

        audio = np.clip(
            audio,
            -1.0,
            1.0
        )

        # ----------------------------------------------
        # FLOAT32 → SIGNED 16-BIT PCM
        # ----------------------------------------------

        pcm16 = (
            audio * 32767
        ).astype(
            np.int16
        )

        pcm_bytes = pcm16.tobytes()

        print(
            f"Generated PCM: "
            f"{len(pcm_bytes)} bytes"
        )

        return pcm_bytes

    # ==================================================
    # GENERATE CHUNKS ONE BY ONE
    #
    # This is the method used by /api/tts.
    #
    # It yields each PCM chunk immediately instead
    # of waiting for all chunks to finish.
    # ==================================================

    def generate_chunks(
        self,
        text: str
    ):
        text = clean_text_for_tts(text)

        if not text:
            return

        start_time = time.perf_counter()

        # ----------------------------------------------
        # SPLIT TEXT
        # ----------------------------------------------

        chunks = self.split_text(
            text,
            max_chars=180
        )

        print()
        print("=" * 60)
        print("GROQ TTS STREAM")
        print("=" * 60)

        print(
            f"Original text: "
            f"{len(text)} characters"
        )

        print(
            f"TTS chunks: "
            f"{len(chunks)}"
        )

        # ----------------------------------------------
        # GENERATE AND YIELD EACH CHUNK
        # ----------------------------------------------

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            print()
            print(
                f"Generating chunk "
                f"{index}/{len(chunks)}"
            )

            print(
                f"Text ({len(chunk)} chars):"
            )

            print(chunk)

            chunk_start = (
                time.perf_counter()
            )

            pcm = self._generate_chunk(
                chunk
            )

            chunk_time = (
                time.perf_counter()
                - chunk_start
            )

            print(
                f"Chunk {index} generated "
                f"in {chunk_time:.3f}s"
            )

            print(
                f"Yielding chunk {index} "
                f"to HTTP stream..."
            )

            # ------------------------------------------
            # THIS IS THE IMPORTANT PART
            #
            # The chunk is sent immediately.
            # We DON'T wait for the remaining
            # chunks.
            # ------------------------------------------

            yield pcm

        total_time = (
            time.perf_counter()
            - start_time
        )

        print()
        print(
            f"Total TTS generation time: "
            f"{total_time:.3f}s"
        )

        print("=" * 60)

    # ==================================================
    # OLD FULL GENERATION METHOD
    #
    # Kept for compatibility/testing.
    #
    # This waits for every chunk and combines them.
    # /api/tts will NOT use this method.
    # ==================================================

    def generate(
        self,
        text: str
    ) -> bytes:

        text = text.strip()

        if not text:
            return b""

        audio_chunks = []

        for pcm in self.generate_chunks(
            text
        ):

            audio_chunks.append(
                pcm
            )

        if not audio_chunks:
            return b""

        return b"".join(
            audio_chunks
        )