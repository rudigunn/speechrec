import os
import requests
from time import sleep, time
import pyaudio
import wave
from constants import openaiAPI

headers = {
    "Authorization": f'Bearer {openaiAPI}',
}

data = {
    "model": "tts-1-hd",
    "input": "This is a test with a long text which is hard to translate to speech. But I will do my best to do it. Please have some patience.",
    "voice": "nova",
    "response_format": "wav",
}

start_time = time()
response = requests.post('https://api.openai.com/v1/audio/speech', headers=headers, json=data, stream=True)

CHUNK_SIZE = 1024

if response.ok:
    with wave.open(response.raw, 'rb') as wf:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        while len(data := wf.readframes(CHUNK_SIZE)): 
            stream.write(data)

        # Sleep to make sure playback has finished before closing
        sleep(1)
        stream.close()
        p.terminate()
else:
    response.raise_for_status()