"""
Enhanced speech recognition handler for multiple platforms.
Automatically selects the best speech recognition method based on platform.
"""
import os
import platform
import sys

# Check platform
if platform.system() == 'Windows':
    # Use simplified Windows speech recognition
    from .simple_windows_speech import speech_recognition_with_fallback as record_speech
    SPEECH_ENGINE = "Windows简化语音引擎"
else:
    # Use standard speech recognition for other platforms
    from .real_speech_to_text import record_and_transcribe as record_speech
    SPEECH_ENGINE = "标准语音引擎"

def record_and_transcribe(duration=5, language="zh-CN"):
    """
    Platform-agnostic speech recognition function.
    Automatically selects the best speech recognition method.
    
    Args:
        duration: Maximum recording duration in seconds
        language: Language code for recognition
        
    Returns:
        str: Transcribed text
    """
    print(f"使用语音引擎: {SPEECH_ENGINE}")
    
    try:
        # Call the appropriate platform-specific function
        text = record_speech(duration=duration, language=language)
        return text
    except Exception as e:
        print(f"语音识别错误: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to text input
        print("\n语音识别失败，请直接输入文字:")
        try:
            text = input("> ")
            return text
        except (EOFError, KeyboardInterrupt):
            print("\n输入被中断")
            return ""

# For testing
if __name__ == "__main__":
    print("测试语音识别...")
    text = record_and_transcribe()
    print(f"识别结果: '{text}'")
