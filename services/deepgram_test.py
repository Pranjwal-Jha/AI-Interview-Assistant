# Install the Deepgram Python SDK # pip install deepgram-sdk==3.*
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
AUDIO_FILE = "Recording3.mp3"

def transcription_service_deepgram(audio):
    try:
        deepgram = DeepgramClient("")
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
