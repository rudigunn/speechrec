import re
from deepgram import (
    DeepgramClient,
    SpeakOptions,
)
from pydub import AudioSegment
from pydub.playback import play
from constants import deepgramAPI

input_text = "Our story begins in a peaceful woodland kingdom where a lively squirrel named Frolic made his abode high up within a cedar tree's embrace. He was not a usual woodland creature, for he was blessed with an insatiable curiosity and a heart for adventure. Nearby, a glistening river snaked through the landscape, home to a wonder named Splash - a silver-scaled flying fish whose ability to break free from his water-haven intrigued the woodland onlookers. This magical world moved on a rhythm of its own until an unforeseen circumstance brought Frolic and Splash together. One radiant morning, while Frolic was on his regular excursion, and Splash was making his aerial tours, an unpredictable wave playfully tossed and misplaced Splash onto the riverbank. Despite his initial astonishment, Frolic hurriedly and kindly assisted his new friend back to his watery abode. Touched by Frolic's compassion, Splash expressed his gratitude by inviting his friend to share his world. As Splash perched on Frolic's back, he tasted of the forest's bounty, felt the sun’s rays filter through the colors of the trees, experienced the conversations amidst the woods, and while at it, taught the woodland how to blur the lines between earth and water."

def chunk_text_by_sentence(text):
    # Find sentence boundaries using regular expression
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]

    chunks = []
    start = 0
    # Split the text into chunks based on sentence boundaries
    for boundary_index in boundaries_indices:
        chunks.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    chunks.append(text[start:].strip())

    return chunks

def synthesize_audio(text):
    # Create a Deepgram client using the API key
    deepgram = DeepgramClient(api_key=deepgramAPI)
    # Choose a model to use for synthesis
    options = SpeakOptions(
            model="aura-helios-en",
        )
    speak_options = {"text": text}
    # Synthesize audio and stream the response
    response =  deepgram.speak.v("1").stream(speak_options, options)
    # Get the audio stream from the response
    audio_buffer = response.stream
    audio_buffer.seek(0)
    # Load audio from buffer using pydub
    audio = AudioSegment.from_mp3(audio_buffer)

    return audio

def main():
    # Chunk the text into smaller parts
    chunks = chunk_text_by_sentence(input_text)

    # Synthesize each chunk into audio and play the audio
    for chunk_text in chunks:
        audio = synthesize_audio(chunk_text)
        play(audio)

if __name__ == "__main__":
    main()

