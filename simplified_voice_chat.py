"""
Simplified Voice Conversation Assistant
---------------------------------------
Core functionality:
1. Voice/Text input
2. AI processing
3. Direct voice output in current window
"""
import os
import sys
import time
import pathlib
import pygame
from dotenv import load_dotenv

# Import voice assistant modules
from voice_assistant.real_speech_to_text import record_and_transcribe
from voice_assistant.text_to_speech import synthesize_speech
from voice_assistant.ai_service import generate_response

# Load environment variables
load_dotenv()

# Set up directory for audio files
data_dir = pathlib.Path("data")
data_dir.mkdir(exist_ok=True)

# Initialize pygame mixer for audio playback
pygame.init()
pygame.mixer.init()

def play_audio(audio_path):
    """Play audio file using pygame directly in the current window."""
    try:
        print(f"Playing audio response...")
        # Make sure the path exists
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False
            
        # Stop any currently playing audio
        pygame.mixer.music.stop()
        
        # Load and play the audio file
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        print("Audio playback completed")
        return True
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False

def voice_chat():
    """Simple voice chat implementation."""
    messages = [{"role": "system", "content": "You are a helpful assistant. Please answer concisely."}]
    count = 0
    exit_phrases = {"exit", "quit", "bye", "结束", "退出", "再见"}
    
    print("\n===== Simplified Voice Chat =====")
    print("- Speak or type your message")
    print("- Say 'exit' to quit")
    print("================================\n")
    
    while True:
        count += 1
        
        # Get user input (voice or text)
        print("\n[Your turn]")
        try:
            # Try voice input first
            print("Listening... (speak now)")
            user_text = record_and_transcribe(duration=5, language="zh-CN")
            
            # Fall back to text if voice recognition fails
            if not user_text:
                print("Voice not recognized. Please type your message:")
                user_text = input("> ")
        except Exception as e:
            print(f"Error with voice input: {e}")
            print("Please type your message instead:")
            user_text = input("> ")
            
        print(f"\nYou: {user_text}")
        
        # Check for exit command
        if any(phrase in user_text.lower() for phrase in exit_phrases):
            print("Exiting voice chat.")
            break
            
        # Send to AI and get response
        messages.append({"role": "user", "content": user_text})
        print("Processing...")
        ai_response = generate_response(messages)
        print(f"\nAssistant: {ai_response}")
        messages.append({"role": "assistant", "content": ai_response})
        
        # Convert to speech and play directly
        print("Generating audio response...")
        audio_file = f"response_{count}.mp3"
        synthesize_speech(ai_response, audio_file)
        
        # Play the audio directly in the current window
        audio_path = str(data_dir / audio_file)
        play_audio(audio_path)
        
        print("\n--------------------------------")

if __name__ == "__main__":
    try:
        voice_chat()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("\nVoice chat ended. Goodbye!")
