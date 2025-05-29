# SpeechRec

A Python project for speech recognition and text-to-speech synthesis using OpenAI and Deepgram APIs.

## Features

- Listens to microphone input and transcribes speech to text (German, de-DE).
- Sends transcribed text to an OpenAI assistant and processes responses.
- Synthesizes assistant responses to speech using Deepgram's TTS.
- Plays a start sequence sound on launch.
- Extracts structured data from assistant responses and saves as JSON.

## Requirements

- Python 3.8+
- [OpenAI API Key](https://platform.openai.com/)
- [Deepgram API Key](https://deepgram.com/)
- Microphone

## Installation

1. Clone the repository.
2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

    If `requirements.txt` is missing, install manually:

    ```sh
    pip install openai deepgram-sdk pydub pygame SpeechRecognition typing_extensions
    ```

3. Add your API keys and assistant ID to `constants.py`:

    ```python
    openaiAPI = "your-openai-api-key"
    deepgramAPI = "your-deepgram-api-key"
    assistantID = "your-assistant-id"
    ```

## Usage

- To start the main speech recognition and assistant workflow:

    ```sh
    python main.py
    ```

- To test Deepgram TTS and audio chunking:

    ```sh
    python playgorund.py
    ```

## Files

- `main.py` - Main application logic.
- `playgorund.py` - Playground for TTS and audio chunking.
- `constants.py` - API keys and configuration.
- `extracted_data.json` - Output file for extracted structured data.
- `start_sequence.mp3` - Startup sound.
- `.gitignore` - Git ignore rules.

## Notes

- Make sure your microphone is connected and working.
- The assistant response should include structured data between `&& ... &&` for extraction.
- Audio playback uses `pygame` and `pydub`.

## License

MIT License (add your license here)