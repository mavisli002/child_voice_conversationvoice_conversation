"""Real speech-to-text module using PyAudio and SpeechRecognition."""
import os
import time
import speech_recognition as sr
from datetime import datetime


class SpeechRecognizer:
    """Class for handling real-time speech recognition."""
    
    def __init__(self, language="zh-CN", timeout=5, phrase_time_limit=None):
        """
        Initialize the speech recognizer.
        
        Args:
            language: Language code for recognition
            timeout: Maximum seconds to wait before giving up
            phrase_time_limit: Maximum seconds for a single phrase
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Adjust for ambient noise level
        self.energy_threshold = 300  # Default value
        self.dynamic_energy_threshold = True
        
    def adjust_for_ambient_noise(self, duration=1):
        """
        Adjust the recognizer sensitivity to ambient noise.
        
        Args:
            duration: Number of seconds to sample ambient noise
        """
        print(f"Adjusting for ambient noise... (Please be quiet for {duration} seconds)")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.energy_threshold = self.recognizer.energy_threshold
            print(f"Energy threshold set to {self.energy_threshold}")
    
    def recognize_from_microphone(self):
        """
        Recognize speech from microphone.
        
        Returns:
            str: Recognized text, or empty string if recognition failed
        """
        print(f"\n🎤 系统已就绪，随时可以开始说话...")
        
        try:
            print("\n📻 正在初始化麦克风...")
            try:
                # Get list of microphone devices
                mic_list = sr.Microphone.list_microphone_names()
                print(f"\nℹ️ 可用麦克风: {len(mic_list)} 个")
                
                if not mic_list:
                    print("\n❌ 未检测到麦克风。请检查您的麦克风连接。")
                    return ""
                
                # Try to find a suitable microphone - prefer ones with "array" in the name
                mic_index = None
                for i, name in enumerate(mic_list):
                    if "麦克风阵列" in name.lower() and "input" not in name.lower():
                        mic_index = i
                        print(f"\n✅ 已选择麦克风: {name} (index {i})")
                        break
                
                # Use the selected microphone or default
                if mic_index is not None:
                    print(f"\n🎤 正在使用麦克风 {mic_index}")
                    with sr.Microphone(device_index=mic_index) as source:
                        print("\n✅ 麦克风初始化成功")
                        # Configure recognizer
                        self.recognizer.energy_threshold = self.energy_threshold
                        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                        
                        print("\n🔊 等待检测到语音...")
                        # Remove timeout for phrase to start to give user more time
                        # Only use phrase_time_limit to limit the length of the recording
                        print("\n🔴 准备录音中... 请开始说话")
                        start_time = time.time()
                        
                        # Add a message that we're listening
                        print("\n🔵 正在倒听您的话语...", end="", flush=True)
                        
                        audio = self.recognizer.listen(
                            source,
                            phrase_time_limit=min(self.phrase_time_limit, 15) if self.phrase_time_limit else 15
                        )
                        duration = time.time() - start_time
                        print(f"\n\n✅ 已捕捉音频 ({duration:.1f}秒)")
                        print("\n🔍 正在识别语音...")
                else:
                    print("\n🎤 使用默认麦克风")
                    with sr.Microphone() as source:
                        print("\n✅ 麦克风初始化成功")
                        # Configure recognizer
                        self.recognizer.energy_threshold = self.energy_threshold
                        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                        
                        print("\n🔊 等待检测到语音...")
                        # Remove timeout for phrase to start to give user more time
                        # Only use phrase_time_limit to limit the length of the recording
                        print("\n🔴 准备录音中... 请开始说话")
                        start_time = time.time()
                        
                        # Add a message that we're listening
                        print("\n🔵 正在倒听您的话语...", end="", flush=True)
                        
                        audio = self.recognizer.listen(
                            source,
                            phrase_time_limit=min(self.phrase_time_limit, 15) if self.phrase_time_limit else 15
                        )
                        duration = time.time() - start_time
                        print(f"\n\n✅ 已捕捉音频 ({duration:.1f}秒)")
                        print("\n🔍 正在识别语音...")
            except Exception as mic_error:
                print(f"Microphone error: {mic_error}")
                return ""
                
            # Try to recognize with Google's speech recognition API
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Recognized: {text}")
                return text
            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"Recognition error: {e}")
                return ""
                
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return ""
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def recognize_from_file(self, audio_file):
        """
        Recognize speech from an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            str: Recognized text, or empty string if recognition failed
        """
        if not os.path.exists(audio_file):
            print(f"Audio file not found: {audio_file}")
            return ""
            
        print(f"Recognizing speech from file: {audio_file}")
        
        try:
            # Load audio file
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
            # Try to recognize with Google's speech recognition API
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"Recognition error: {e}")
                return ""
                
        except Exception as e:
            print(f"Error during file recognition: {e}")
            return ""


def record_and_transcribe(duration=5, language="zh-CN"):
    """
    Record audio from microphone and transcribe it to text.
    
    Args:
        duration: Maximum recording duration in seconds
        language: Language code for recognition
        
    Returns:
        str: Transcribed text
    """
    try:
        print("\n🔊 正在初始化语音识别系统...")
        # Initialize recognizer
        recognizer = SpeechRecognizer(
            language=language,
            timeout=duration,
            phrase_time_limit=duration
        )
        
        # Adjust for ambient noise (optional)
        try:
            recognizer.adjust_for_ambient_noise(duration=1)
        except Exception as e:
            print(f"\n⚠️ 无法调整环境噪音: {e}")
        
        # Recognize speech
        print("\n🔊 正在等待您说话...")
        text = recognizer.recognize_from_microphone()
        if text:
            print(f"\n✅ 语音识别成功")
        return text
        
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        
        # Fallback to text input if speech recognition fails
        print("\nSpeech recognition failed. Please type your message instead:")
        try:
            text = input("> ")
            return text
        except (EOFError, KeyboardInterrupt):
            print("\nInput interrupted.")
            return ""


# Test function
if __name__ == "__main__":
    print("Testing speech recognition...")
    text = record_and_transcribe(duration=5)
    print(f"Final result: '{text}'")
