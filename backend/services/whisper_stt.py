
from faster_whisper import WhisperModel


class WhisperSTT:

    def __init__(self):
        print("Loading Whisper model...")

        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8",
        )

        print("Whisper model loaded.")

    def transcribe(self, audio_path: str) -> str:

        segments, info = self.model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt=(
                "Webenza is spelled W-E-B-E-N-Z-A. "
                "Webenza is a company. "
                "Webenza services and Webenza website."
            ),
        )

        # IMPORTANT:
        # faster-whisper returns a generator.
        # Iterating over it actually performs transcription.
        text_parts = []

        for segment in segments:
            text_parts.append(
                segment.text.strip()
            )

        text = " ".join(text_parts).strip()

        print("Whisper transcript:", text)

        return text