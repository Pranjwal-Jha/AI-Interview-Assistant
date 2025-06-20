import speech_recognition as sr
import whisper
import torch
import numpy as np
import text_preprocess
import lm_request
import gemini_pdf_test
import suppress_alsa_error
import ollama_request
# for index,name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"Microphone with name {name} found for device index : {index}")
WHISPER_MODEL="small"
WHISPER_SAMPLE_RATE=16000
LISTEN_TIMEOUT=5
PHRASE_TIME_LIMIT=20

#gpu cleaned_text
device="cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device -> {device}")


def load_whisper(model_name="small"):
    print(f"Loading the model -> {model_name} on {device}")
    try:
        model=whisper.load_model(model_name,device=device)
        print("Model Loaded Successfully")
        return model
    except Exception as e:
        print(f"exception occured loading the model -> {e}")

def initialise_audio():
    recogniser=sr.Recognizer()
    # recogniser.energy_threshold=500:
    recogniser.pause_threshold=3
    #recogniser.non_speaking_duration=0.5 #look into this more
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

whisper_model=load_whisper(WHISPER_MODEL)
if whisper_model is not None:
    print("The model is loaded Successfully")
with suppress_alsa_error.no_alsa_errors():
    mic,rec= initialise_audio()
print("\nInitialization Complete, ready to start listening")
print(f"\nSay {'stop listening'.upper()} to exit\n")

def transcribe_text(model,microphone,recogniser,timeout_seconds,phrase_tl):
    with microphone as source:
        print("\n\n","-"*10,"Say -> Stop Listening <- To exit","-"*10)
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
                audio_tensor=torch.from_numpy(audio_normalised).to(device)
                result=model.transcribe(audio_tensor,fp16=False)

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


try:
    gemini_pdf_test.initialize_conversation()
    while True:
        transcribed_text=transcribe_text(model=whisper_model,microphone=mic,recogniser=rec,timeout_seconds=LISTEN_TIMEOUT,phrase_tl=PHRASE_TIME_LIMIT)
        if transcribed_text:
            cleaned_text=text_preprocess.preprocess_words(transcribed_text)
            print(f"\n\nYou've Said ---> {cleaned_text}")
            sentences=cleaned_text.split(". ")
            for sentence in sentences:
                if "stop listening" in sentence and len(sentence.split()) < 5:
                    gemini_pdf_test.clear_history_file()
                    exit()
            print("-"*15,"Response","-"*15)
            print(gemini_pdf_test.gemini_response(cleaned_text))
            # print(ollama_request.streaming_response(cleaned_text))
            print("-"*15,"END","-"*15)
except Exception as e:
    print(f"exception occured -> {e}")
