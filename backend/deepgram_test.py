from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import os

AUDIO_FILE = "Recording3.mp3"

def transcription_service_deepgram(audio):
    try:
        deepgram_api_key=os.environ.get("DEEPGRAM_API_KEY")
        if not deepgram_api_key:
            print("Error no API key for Deepgram")
            return None
        deepgram = DeepgramClient(deepgram_api_key)
        payload: FileSource = {
            "buffer": audio,
        }

        options = PrerecordedOptions(
            model="nova-3",
            smart_format=True,
        )

        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        return response["results"]["channels"][0]["alternatives"][0]['transcript']

    except Exception as e:
        print(f"Exception: {e}")
        return None
