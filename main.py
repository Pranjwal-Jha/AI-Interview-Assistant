import speech_recognition as sr
import time
import whisper
import torch
import numpy as np
# for index,name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"Microphone with name {name} found for device index : {index}")
WHISPER_MODEL="small"
WHISPER_SAMPLE_RATE=16000
LISTEN_TIMEOUT=5
PHRASE_TIME_LIMIT=20

def load_whisper(model_name="small"):
    print(f"Loading the model -> {model_name} on CPU")
    try:
        model=whisper.load_model(model_name,device="cpu")
        print("Model Loaded Successfully")
        return model
    except Exception as e:
        print(f"exception occured loading the model -> {e}")

def initialise_audio():
    recogniser=sr.Recognizer()
    # recogniser.energy_threshold=500
    print("Recognizer instance created\n\n")

    default_mic=None
    try:
        default_mic=sr.Microphone(sample_rate=16000)
        print("Default Mic initialised !\n\n")
    except Exception as e:
        print(f"An exception occured -> {e}")

    if default_mic is None:
        print("Failed to initialise a microphone.")

    print("-"*20)

    if default_mic is not None:
        with default_mic as source:
            try:
                recogniser.adjust_for_ambient_noise(source,duration=2)
                print("\nAmbient noise calibration completion, proceed with speaking\n")
                return default_mic,recogniser
            except Exception as e:
                print(f"exception occured while Ambient noise calibration -> {e}")
    print('-ERROR-'*5)
    return None,None

def transcribe_text(model,microphone,recogniser,timeout_seconds,phrase_tl):
    with microphone as source:
        print("\nAdjusting for ambient noise...\n")
        recogniser.adjust_for_ambient_noise(source,duration=2)
        print(f"Start Speaking, Timeout -> {timeout_seconds}, Time Limit for speaking -> {phrase_tl}")
        
        audio_data=None
        try:
            audio_data=recogniser.listen(source,timeout=timeout_seconds,phrase_time_limit=phrase_tl)
            print("Processing speech...")
        except sr.WaitTimeoutError:
            return None
        
        if audio_data:
            try:
                raw_data=audio_data.get_raw_data(convert_rate=WHISPER_SAMPLE_RATE,convert_width=2)
                audio_np=np.frombuffer(raw_data,dtype=np.int16)
                audio_normalised=audio_np.astype(np.float32)/32768.0
                result=model.transcribe(audio_normalised,fp16=False)

                text=result["text"].strip()
                if text and len(text)>1:
                    return text.lower()
                else:
                    print("whisper returned empty or very short text")
                    return None
            except Exception as e:
                print(f"Exception occured during transcription -> {e}")
                return None
        else:
            return None


whisper_model=load_whisper(WHISPER_MODEL)
if whisper_model is not None:
    print("The model is loaded Successfully")
mic,rec= initialise_audio()

print("\nInitialization Complete, ready to start listening")
print(f"\nSay {'stop listening'.upper()} to exit\n")

try:
    while True:
        transcribed_text=transcribe_text(model=whisper_model,microphone=mic,recogniser=rec,timeout_seconds=LISTEN_TIMEOUT,phrase_tl=PHRASE_TIME_LIMIT)
        if transcribed_text:
            print(f"\n\nYou've Said ---> {transcribed_text}")
except Exception as e:
    print(f"exception occured -> {e}")

        
