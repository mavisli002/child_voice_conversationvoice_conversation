"""
Windows-optimized speech recognition module.
Provides multiple recognition methods for Windows systems:
1. Google online recognition
2. Offline recognition
3. Windows native speech recognition
"""
import os
import time
import platform
import speech_recognition as sr
from datetime import datetime

# Windows-specific imports - only import if on Windows
if platform.system() == 'Windows':
    try:
        import win32com.client
        import comtypes.client
        import pythoncom
        WINDOWS_SPEECH_AVAILABLE = True
    except ImportError:
        WINDOWS_SPEECH_AVAILABLE = False
else:
    WINDOWS_SPEECH_AVAILABLE = False


class WindowsSpeechRecognizer:
    """Windows-optimized speech recognizer with multiple fallback methods."""
    
    def __init__(self, language="zh-CN", timeout=5, phrase_time_limit=None):
        """
        Initialize the speech recognizer with Windows-specific optimizations.
        
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
        
        # Check if Windows speech is available
        self.windows_speech_available = WINDOWS_SPEECH_AVAILABLE
        if self.windows_speech_available:
            try:
                # Initialize Windows Speech Recognition
                pythoncom.CoInitialize()
                self.win_speech = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
                self.win_context = self.win_speech.CreateRecoContext()
                self.win_grammar = self.win_context.CreateGrammar()
                self.win_grammar.DictationSetState(1)  # Activate dictation
                print("Windows Speech Recognition initialized successfully")
            except Exception as e:
                print(f"Error initializing Windows Speech Recognition: {e}")
                self.windows_speech_available = False
        
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
    
    def _recognize_with_windows_native(self, max_duration=10):
        """
        Use Windows native speech recognition API.
        
        Args:
            max_duration: Maximum recording duration in seconds
            
        Returns:
            str: Recognized text, or empty string if recognition failed
        """
        if not self.windows_speech_available:
            print("Windows Speech Recognition not available")
            return ""
            
        try:
            print("Using Windows native speech recognition...")
            pythoncom.CoInitialize()
            
            # Create a simple dictation grammar
            voice = comtypes.client.CreateObject("SAPI.SpVoice")
            voice.Speak("Ready to listen", 0)
            
            # Setup recognition context
            context = win32com.client.Dispatch("SAPI.SpInProcRecoContext")
            grammar = context.CreateGrammar()
            grammar.DictationSetState(1)  # Enable dictation
            
            # Listen for speech
            print("Listening for Windows native speech...")
            start_time = time.time()
            result = ""
            
            while time.time() - start_time < max_duration:
                time.sleep(0.1)  # Small delay to prevent high CPU usage
                # Check if speech is recognized
                if context.Recognition:
                    result = context.Recognition.PhraseInfo.GetText()
                    break
            
            if result:
                print(f"Windows recognized: {result}")
                return result
            else:
                print("No speech detected with Windows recognition")
                return ""
                
        except Exception as e:
            print(f"Error with Windows speech recognition: {e}")
            return ""
            
    def recognize_from_microphone(self):
        """
        Recognize speech from microphone with multiple fallback methods.
        
        Returns:
            str: Recognized text, or empty string if recognition failed
        """
        print(f"\n🎤 系统已就绪，随时可以开始说话...")
        
        try:
            print("\n📻 正在初始化麦克风...")
            # Try to find a suitable microphone
            try:
                # Get list of microphone devices
                mic_list = sr.Microphone.list_microphone_names()
                print(f"\nℹ️ 可用麦克风: {len(mic_list)} 个")
                
                if not mic_list:
                    print("\n❌ 未检测到麦克风。请检查您的麦克风连接。")
                    return ""
                
                # Try to find a suitable microphone - prefer ones with specific names
                mic_index = None
                preferred_names = ["麦克风阵列", "array", "realtek", "microphone"]
                
                # First pass - look for preferred names
                for i, name in enumerate(mic_list):
                    for preferred in preferred_names:
                        if preferred.lower() in name.lower():
                            mic_index = i
                            print(f"\n✅ 已选择麦克风: {name} (index {i})")
                            break
                    if mic_index is not None:
                        break
                
                # If no preferred microphone found, use the default
                if mic_index is None:
                    print(f"\n✅ 使用默认麦克风")
                
                # Use the selected microphone or default
                with sr.Microphone(device_index=mic_index) as source:
                    print("\n✅ 麦克风初始化成功")
                    # Configure recognizer
                    self.recognizer.energy_threshold = self.energy_threshold
                    self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                    
                    print("\n🔊 等待检测到语音...")
                    print("\n🔴 准备录音中... 请开始说话")
                    
                    # Add a message that we're listening
                    print("\n🔵 正在倒听您的话语...", end="", flush=True)
                    
                    audio = self.recognizer.listen(
                        source,
                        phrase_time_limit=min(self.phrase_time_limit, 15) if self.phrase_time_limit else 15
                    )
                    
                    print("\n🔍 正在识别语音...")
            except Exception as mic_error:
                print(f"Microphone error: {mic_error}")
                return ""
            
            # METHOD 1: Try to recognize with Google's speech recognition API
            try:
                print("Attempting Google Speech Recognition...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Google recognized: {text}")
                if text:
                    return text
            except sr.UnknownValueError:
                print("Google could not understand audio")
            except sr.RequestError as e:
                print(f"Google recognition error: {e}")
            
            # METHOD 2: Try offline recognition if Google fails
            try:
                print("Attempting offline recognition with Sphinx...")
                # Sphinx works best with English, so we use it as fallback
                offline_text = self.recognizer.recognize_sphinx(audio)
                print(f"Sphinx recognized: {offline_text}")
                if offline_text:
                    return offline_text
            except:
                print("Sphinx recognition failed or not available")
            
            # METHOD 3: Try Windows native speech recognition as last resort
            if self.windows_speech_available:
                windows_text = self._recognize_with_windows_native()
                if windows_text:
                    return windows_text
            
            # If all methods fail
            print("All speech recognition methods failed")
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
                
            # Try multiple recognition methods
            
            # METHOD 1: Google
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"Google recognized: {text}")
                if text:
                    return text
            except:
                print("Google recognition failed")
            
            # METHOD 2: Sphinx (offline)
            try:
                offline_text = self.recognizer.recognize_sphinx(audio)
                print(f"Sphinx recognized: {offline_text}")
                if offline_text:
                    return offline_text
            except:
                print("Sphinx recognition failed or not available")
            
            # If all methods fail
            print("All file recognition methods failed")
            return ""
                
        except Exception as e:
            print(f"Error during file recognition: {e}")
            return ""


def windows_record_and_transcribe(duration=5, language="zh-CN"):
    """
    Record audio from microphone and transcribe it to text using Windows-optimized methods.
    
    Args:
        duration: Maximum recording duration in seconds
        language: Language code for recognition
        
    Returns:
        str: Transcribed text
    """
    try:
        print("\n🔊 正在初始化Windows语音识别系统...")
        # Initialize recognizer
        recognizer = WindowsSpeechRecognizer(
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
            print(f"\n✅ 语音识别成功: {text}")
            return text
        else:
            print("\n❌ 语音识别失败")
            
            # Fallback to text input if speech recognition fails
            print("\n请直接输入您的消息:")
            try:
                text = input("> ")
                return text
            except (EOFError, KeyboardInterrupt):
                print("\n输入中断。")
                return ""
        
    except Exception as e:
        print(f"语音识别错误: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to text input if speech recognition fails
        print("\n语音识别失败。请直接输入您的消息:")
        try:
            text = input("> ")
            return text
        except (EOFError, KeyboardInterrupt):
            print("\n输入中断。")
            return ""


# Test function
if __name__ == "__main__":
    print("Testing Windows-optimized speech recognition...")
    text = windows_record_and_transcribe(duration=5)
    print(f"Final result: '{text}'")
