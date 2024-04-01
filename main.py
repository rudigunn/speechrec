import json
import os
import re
import time
from queue import Queue

import pygame
import speech_recognition as sr
from openai import OpenAI
from constants import openaiAPI, assistantID

r = sr.Recognizer()
client = OpenAI(api_key=openaiAPI)
pygame.mixer.init()
data_queue = Queue()


def record_callback(_, audio: sr.AudioData) -> None:
    """
    Threaded callback function to receive audio data when recordings finish.
    audio: An AudioData containing the recorded bytes.
    """
    data_queue.put(audio)


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


def send_message_and_get_response(text, thread):
    """Function to send user message and get response from OpenAI."""
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistantID
    )

    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(0.1)  # Wait for 0.1 second
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    if run.status == 'completed':
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
        else:
            extracted_text = ""

        response_text = re.sub(r'&&(.+?)&&', '', response_text, flags=re.DOTALL).strip()
        print(response_text)

        with client.audio.speech.with_streaming_response.create(
                model="tts-1-hd",
                voice="nova",
                input=f"{response_text}",
                response_format="mp3"
        ) as response:
            response.stream_to_file("output.mp3")

        play_music("output.mp3")
        os.remove("output.mp3")

        if extracted_text:
            exit(0)
    else:
        print(run.status)


def main():
    """Function to listen to audio, transcribe it, and get a response."""
    source = sr.Microphone(sample_rate=16000)

    with source:
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Calibration done. You can speak now.")

    r.dynamic_energy_threshold = False
    r.energy_threshold = 1000

    thread = client.beta.threads.create()
    r.listen_in_background(source, callback=record_callback, phrase_time_limit=25)
    play_music("start_sequence.mp3")
    data_queue.queue.clear()

    while True:
        try:
            if data_queue.qsize() != 0:
                audio = data_queue.get()
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
