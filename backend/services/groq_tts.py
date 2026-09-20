import io
import re
import time
import wave

from pathlib import Path

import numpy as np
from groq import Groq
from scipy.signal import resample_poly

from backend.config import groq_api_key
def clean_text_for_tts(text: str) -> str:
    if not text:
        return ""

    # Remove bold Markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)

    # Remove italic Markdown
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"\1",
        text
    )

    # Remove inline code
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove Markdown links but preserve visible text
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove Markdown headings
    text = re.sub(
        r"^\s*#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Convert line breaks and repeated whitespace into spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

class GroqTTS:

    def __init__(
        self,
        model="canopylabs/orpheus-v1-english",
        voice="autumn",
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
        max_chars: int = 220,
        min_chars: int = 80,
    ) -> list[str]:

        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        # First combine normal sentences.
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # Handle a sentence longer than max_chars.
            if len(sentence) > max_chars:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                words = sentence.split()
                word_chunk = ""

                for word in words:
                    candidate = f"{word_chunk} {word}".strip()

                    if len(candidate) <= max_chars:
                        word_chunk = candidate
                    else:
                        if word_chunk:
                            chunks.append(word_chunk)

                        word_chunk = word

                if word_chunk:
                    chunks.append(word_chunk)

                continue

            candidate = f"{current_chunk} {sentence}".strip()

            if len(candidate) <= max_chars:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # Merge short chunks where possible.
        merged_chunks = []
        current_chunk = ""

        for chunk in chunks:
            if not current_chunk:
                current_chunk = chunk
                continue

            candidate = f"{current_chunk} {chunk}".strip()

            if (
                len(current_chunk) < min_chars
                and len(candidate) <= max_chars
            ):
                current_chunk = candidate
            else:
                merged_chunks.append(current_chunk)
                current_chunk = chunk

        if current_chunk:
            merged_chunks.append(current_chunk)

        return merged_chunks


    # ==================================================
    # GENERATE ONE TTS CHUNK
    # ==================================================

    def _generate_chunk(self,text: str):

        print(
            f"Generating Groq TTS chunk "
            f"({len(text)} characters)"
        )

        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            response_format="wav",
            speed=1.8,

        )

        wav_bytes = response.read()

        from pathlib import Path

        debug_original_path = (
            Path(__file__).resolve().parent
            / "debug"
            / "debug_groq_original.wav"
        )

        debug_original_path.parent.mkdir(parents=True, exist_ok=True)
        debug_original_path.write_bytes(wav_bytes)

        print("[TTS DEBUG] Original Groq WAV saved to:")
        print(debug_original_path)


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


        audio_duration = len(pcm_bytes) / (16000 * 2)

        print(
            f"Audio duration: "
            f"{audio_duration:.3f}s"
        )
        
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

    def generate_chunks(self,text: str):
        text = clean_text_for_tts(text)

        if not text:
            return

        start_time = time.perf_counter()

        # ----------------------------------------------
        # SPLIT TEXT
        # ----------------------------------------------

        chunks = self.split_text(
            text,
            max_chars=200,
            min_chars=80
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
        # DEBUG:
        # Collect the EXACT PCM that is being
        # yielded to the HTTP stream / Simli
        # ----------------------------------------------

        all_pcm = bytearray()

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

            # ------------------------------------------
            # DEBUG:
            # Store the exact PCM
            # ------------------------------------------

            all_pcm.extend(pcm)

            print(
                f"Yielding chunk {index} "
                f"to HTTP stream..."
            )

            yield pcm

        # ----------------------------------------------
        # DEBUG:
        # Save complete PCM as WAV
        # ----------------------------------------------

        debug_path = (
            Path(__file__).resolve().parent
            / "debug"
            / "debug_tts.wav"
        )

        debug_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with wave.open(
            str(debug_path),
            "wb"
        ) as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(all_pcm)

        print()
        print(
            f"[TTS DEBUG] WAV saved to:"
        )

        print(debug_path)

        # ----------------------------------------------
        # TOTAL TIME
        # ----------------------------------------------

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