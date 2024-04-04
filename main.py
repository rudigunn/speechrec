import os
import re
import threading
import time
import json
import pygame
import speech_recognition as sr

from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
from typing_extensions import override
from constants import openaiAPI, deepgramAPI, assistantID
from openai import OpenAI, AssistantEventHandler
from deepgram import DeepgramClient, SpeakOptions


r = sr.Recognizer()
client = OpenAI(api_key=openaiAPI)
pygame.mixer.init()
stt_queue = Queue()
tts_queue = Queue()
delta_chunks = []


class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    global tts_queue, delta_chunks
    if delta.value.endswith(".") or delta.value.endswith("?") or delta.value.endswith("!"):
        delta_chunks.append(delta.value)
        tts_queue.put(''.join(delta_chunks))
        delta_chunks = []
    else: 
        delta_chunks.append(delta.value)
    print(delta.value, end="", flush=True)

  def on_event(self, event) -> None:
      if event.event == "thread.run.completed":
          global run_status
          run_status = True


def record_callback(_, audio: sr.AudioData) -> None:
    """
    Threaded callback function to receive audio data when recordings finish.
    audio: An AudioData containing the recorded bytes.
    """
    print("Put")
    stt_queue.put(audio)


def play_music(file):
    """Function to play the MP3 file."""
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()


def transcribe_audio(audio):
    """Function to transcribe audio using Google Web Speech API."""
    try:
        return r.recognize_google(audio, language="de-DE")
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Error requesting Google Web Speech API: {e}")
        return ""
    

def synthesize_audio(text, deepgramAPI):
    deepgram = DeepgramClient(api_key=deepgramAPI)
    options = SpeakOptions(model="aura-orion-en")
    speak_options = {"text": text}
    response = deepgram.speak.v("1").stream(speak_options, options)
    audio_buffer = response.stream
    audio_buffer.seek(0)
    audio = AudioSegment.from_mp3(audio_buffer)
    return audio


def tts_worker():
    while True:
        if tts_queue.qsize() != 0:
            sentence = tts_queue.get(block=True, timeout=400)
            if sentence is None:  
                break
            audio = synthesize_audio(sentence, deepgramAPI)
            play(audio)
            print(tts_queue.qsize())
        else:
            time.sleep(0.25)
        

def send_message_and_get_response(text, thread):
    """Function to send user message and get response from OpenAI."""
    global run_status

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )

    with client.beta.threads.runs.create_and_stream(
        thread_id=thread.id,
        assistant_id=assistantID,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    if run_status:
        run_status = False
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        response_text = messages.data[0].content[0].text.value
        extracted_text_match = re.search(r'&&(.+?)&&', response_text, re.DOTALL)

        if extracted_text_match:
            extracted_text = extracted_text_match.group(1).strip()
            json_data = json.loads(extracted_text)
            with open('extracted_data.json', 'w') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            exit(0)
        else:
            extracted_text = ""

        #response_text = re.sub(r'&&(.+?)&&', '', response_text, flags=re.DOTALL).strip()
        #print(response_text)
    else:
        pass


def main():
    """Function to listen to audio, transcribe it, and get a response."""
    source = sr.Microphone(sample_rate=16000)

    with source:
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Calibration done. You can speak now.")

    r.dynamic_energy_threshold = False
    r.energy_threshold = 500

    thread = client.beta.threads.create()
    r.listen_in_background(source, callback=record_callback, phrase_time_limit=25)
    play_music("start_sequence.mp3")
    stt_queue.queue.clear()
    tts_queue.queue.clear()

    threading.Thread(target=tts_worker, daemon=True).start()

    while True:
        try:
            if stt_queue.qsize() != 0:
                audio = stt_queue.get()
                print("Transcribing...")

                text = transcribe_audio(audio)
                print(f"Transcription: {text}")

                if text != "":
                    send_message_and_get_response(text, thread)
            else:
                time.sleep(0.25)

        except KeyboardInterrupt:
            print("Exiting...")
            break


if __name__ == "__main__":
    main()
