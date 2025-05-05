# Voice Conversation Assistant

A simplified voice conversation assistant that focuses on core functionality, providing both text-based and voice-based interaction modes.

## Features

- Dual-mode operation:
  - Text mode: Keyboard input with text output
  - Voice mode: Speech recognition input with voice output
- Speech-to-text conversion using ByteDance's ASR service
- Text-to-speech synthesis using ByteDance's TTS service
- Conversational AI using OpenAI/DeepSeek API
- Conversation history saving
- Organized media storage in data folder

## Project Structure

- `main.py` - Single entry point with both text and voice functionality
- `voice_assistant/` - Package containing core modules:
  - `ai_service.py` - AI conversation handling
  - `real_speech_to_text.py` - Voice input processing
  - `text_to_speech.py` - Voice output generation
  - Other supporting modules
- `data/` - Storage for generated media files and conversation logs
- `run_assistant.bat` - Windows batch file to easily run the application

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with the following variables (or copy from `.env.example`):
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   BASE_URL=your_base_url_here
   ASR_ACCESS_KEY=your_asr_access_key_here
   ASR_APP_KEY=your_asr_app_key_here
   TTS_ACCESS_TOKEN=your_tts_access_token_here
   TTS_APPID=your_tts_appid_here
   ```

## Running the Application

### Option 1: Using the batch file (Windows)

Simply double-click the `run_assistant.bat` file, which will:
- Install required dependencies
- Launch the application

### Option 2: Using Python directly

```
python main.py
```

## Usage

1. When the application starts, you'll be prompted to choose a mode:
   - Option 1: Text-based assistant (keyboard input/text output)
   - Option 2: Voice-based assistant (voice input/voice output)

2. For text mode:
   - Type your messages and press Enter
   - Read the AI's responses on screen
   - Conversation history is saved to the data folder

3. For voice mode:
   - Speak to the assistant when prompted
   - The assistant will respond with synthesized speech
   - Audio responses are saved in the data folder

4. In either mode, say or type "exit", "quit", "bye", or similar phrases to end the conversation

## Requirements

- Python 3.6 or later
- Windows, macOS, or Linux
- Microphone for voice input (voice mode only)
- Internet connection for API access
