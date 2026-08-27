import asyncio

from backend.services.groq_tts import GroqTTS


class TTSStream:

    def __init__(self, tts: GroqTTS):

        self.tts = tts

    async def stream(self, text: str):

        # ------------------------------------------
        # SPLIT RESPONSE
        # ------------------------------------------

        chunks = self.tts.split_text(
            text,
            max_chars=180
        )

        print()
        print("=" * 60)
        print("TTS STREAM")
        print("=" * 60)

        print(
            f"Text length: {len(text)}"
        )

        print(
            f"TTS chunks: {len(chunks)}"
        )

        # ------------------------------------------
        # FIFO QUEUE
        # ------------------------------------------

        queue = asyncio.Queue()

        # ------------------------------------------
        # PRODUCER
        #
        # Generates TTS chunks one by one.
        # ------------------------------------------

        async def producer():

            try:

                for index, chunk in enumerate(
                    chunks,
                    start=1
                ):

                    print(
                        f"\n[TTS PRODUCER] "
                        f"Generating chunk "
                        f"{index}/{len(chunks)}"
                    )

                    # Groq SDK is synchronous.
                    #
                    # Run it in a worker thread so
                    # the async event loop is not blocked.

                    pcm = await asyncio.to_thread(
                        self.tts.generate_chunk,
                        chunk
                    )

                    print(
                        f"[TTS PRODUCER] "
                        f"Chunk {index} ready: "
                        f"{len(pcm)} bytes"
                    )

                    # Put PCM into FIFO queue.

                    await queue.put(
                        pcm
                    )

            finally:

                # None means:
                #
                # "No more chunks."

                await queue.put(
                    None
                )

        # ------------------------------------------
        # CONSUMER
        #
        # Takes chunks from FIFO queue.
        # ------------------------------------------

        async def consumer():

            while True:

                pcm = await queue.get()

                # End signal

                if pcm is None:

                    queue.task_done()

                    break

                try:

                    # Yield PCM to FastAPI.
                    #
                    # The API endpoint will send
                    # this chunk to the browser.

                    yield pcm

                finally:

                    queue.task_done()

        # ------------------------------------------
        # START PRODUCER
        # ------------------------------------------

        producer_task = asyncio.create_task(
            producer()
        )

        try:

            # --------------------------------------
            # CONSUMER LOOP
            # --------------------------------------

            while True:

                pcm = await queue.get()

                if pcm is None:

                    queue.task_done()

                    break

                try:

                    yield pcm

                finally:

                    queue.task_done()

        finally:

            # Make sure producer does not remain
            # running if client disconnects.

            if not producer_task.done():

                producer_task.cancel()

                try:

                    await producer_task

                except asyncio.CancelledError:

                    pass

        print()
        print(
            "=" * 60
        )

        print(
            "TTS STREAM FINISHED"
        )

        print(
            "=" * 60
        )