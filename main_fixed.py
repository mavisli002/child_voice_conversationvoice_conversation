"""
Voice Conversation Assistant
-------------------------------------------
A simplified voice conversation assistant focused on core functionality:
1. Voice/Text input
2. AI processing
3. Voice/Text output
"""
import os
import sys
import io
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

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Set console encoding
try:
    if os.name == 'nt':
        os.system("chcp 65001 >nul")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
except Exception as e:
    print(f"Warning: Could not set encoding: {e}")


def run_voice_assistant(system_prompt="你是一个有帮助的助手"):
    """Run the voice-based assistant with voice input and output."""
    messages = [{"role": "system", "content": system_prompt}]
    
    count = 0
    EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}
    
    print("=" * 50)
    print("Voice Conversation Assistant")
    print("=" * 50)
    print("Instructions:")
    print("- System will prompt you to speak")
    print("- If voice recognition fails, you can type your input")
    print("- Say 'exit' to end the conversation")
    print("=" * 50)
    
    try:
        while True:
            count += 1
            print("\n" + "-" * 40)
            print(f"[Dialog #{count}]")
            print("-" * 40)
            print("\nReady to begin...")
            print("\nPlease start speaking")
            
            # Try to get speech input with a timeout
            try:
                user_text = record_and_transcribe(duration=5, language="zh-CN")
            except Exception as e:
                print(f"\nVoice recognition error: {e}")
                user_text = ""
                
            # If speech recognition failed, fall back to text input
            if not user_text:
                print("\nCould not recognize speech, please type instead:")
                try:
                    print("> ", end="")
                    user_text = input()
                except (EOFError, KeyboardInterrupt):
                    print("\nUser terminated, exiting")
                    break
                    
                if not user_text:
                    print("\nNo input received, please try again")
                    continue
                
            print(f"\nYou said: {user_text}")
            
            # Check if user wants to exit
            if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
                print("\nExit command detected, ending conversation")
                break
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Generate AI response
            start_time = time.time()
            print("\nAI is thinking...", end="", flush=True)
            
            # Generate the response
            ai_response = generate_response(messages)
            
            # Calculate thinking time
            thinking_time = time.time() - start_time
            print(f"\rAI finished thinking ({thinking_time:.1f} seconds)")
            
            # Display the response with proper formatting
            print(f"\nAssistant: {ai_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
            
            # Convert AI response to speech
            print("\nGenerating voice response...")
            mp3_filename = f"response_{count}.mp3"
            
            # Generate speech
            success = synthesize_speech(ai_response, mp3_filename)
            
            if success:
                print("\nVoice response generated successfully")
            else:
                print("\nVoice generation may be incomplete, but will try to play available part")
            
            # Play the generated speech directly using pygame
            try:
                # Get full path to the audio file
                audio_path = str(pathlib.Path("data") / mp3_filename)
                
                if os.path.exists(audio_path):
                    print("\nPlaying voice response...")
                    
                    # Stop any currently playing audio
                    pygame.mixer.music.stop()
                    
                    # Load and play the audio file
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    # Wait for the audio to finish playing
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                        
                    print("\nVoice playback completed")
                else:
                    print(f"\nCould not find audio file: {audio_path}")
            except Exception as e:
                print(f"\nError playing audio: {e}")
                print(f"\nAudio file saved to data/{mp3_filename}")
    
    except KeyboardInterrupt:
        print("\nUser terminated, exiting")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("\n" + "=" * 50)
        print("Voice assistant closed")
        print("=" * 50)


def run_text_assistant(system_prompt="你是一个有帮助的助手", save_conversation=True):
    """Run the text-based assistant with text input and output."""
    # Initialize conversation
    messages = [{"role": "system", "content": system_prompt}]
    
    # Set up variables
    count = 0
    conversation_log = []
    EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}
    
    print("=" * 50)
    print("Text Assistant Started")
    print("=" * 50)
    print("Using text input mode")
    print(f"Type any of these words to end: exit, quit, bye")
    print("-" * 50)
    
    try:
        while True:
            count += 1
            print(f"\n[Dialog #{count}]")
            
            # Get user input (text only)
            try:
                print("\n> ", end="", flush=True)
                user_text = input()
                
                if not user_text:
                    print("No input received, please try again")
                    continue
            except EOFError:
                print("\nInput error, exiting")
                break
            except KeyboardInterrupt:
                print("\nUser terminated, exiting")
                break
                
            print(f"User: {user_text}")
            
            # Save to conversation log
            if save_conversation:
                conversation_log.append(f"User: {user_text}")
            
            # Check if user wants to exit
            if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
                print("Exit command detected, ending conversation")
                break
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Generate AI response
            print("AI is thinking...")
            ai_response = generate_response(messages)
            print(f"Assistant: {ai_response}")
            
            # Save to conversation log
            if save_conversation:
                conversation_log.append(f"Assistant: {ai_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
    
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        print("\n" + "=" * 50)
        print("Text assistant closed")
        print("=" * 50)
        
        # Save conversation history if enabled
        if save_conversation and conversation_log:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"
            
            # Ensure data directory exists
            data_dir = pathlib.Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Save to data directory
            file_path = data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(conversation_log))
            print(f"Conversation history saved to {file_path}")


def main():
    """Main entry point with mode selection."""
    # Create data directory if it doesn't exist
    data_dir = pathlib.Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 50)
    print("Voice Conversation Assistant")
    print("=" * 50)
    print("Please select a mode:")
    print("1. Text Mode (keyboard input/text output)")
    print("2. Voice Mode (voice input/voice output)")
    print("=" * 50)
    
    choice = None
    try:
        print("Enter your choice (1 or 2): ", end="", flush=True)
        choice = input()
    except (EOFError, KeyboardInterrupt):
        print("\nInput error, defaulting to text mode")
        choice = "1"
    
    if choice == "1":
        run_text_assistant(system_prompt="You are a helpful assistant. Please answer questions concisely.")
    elif choice == "2":
        run_voice_assistant(system_prompt="You are a helpful assistant. Please answer questions concisely.")
    else:
        print(f"Invalid choice: '{choice}', please restart the program and select 1 or 2")


if __name__ == "__main__":
    main()
