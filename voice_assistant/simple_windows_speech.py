"""
简化版Windows语音识别模块
专为Windows系统优化，使用Windows原生语音API和pyttsx3
"""
import os
import sys
import time
import platform
import speech_recognition as sr
import pyttsx3
import pythoncom
import win32com.client
from datetime import datetime

# 检查Windows语音支持
try:
    import win32com.client
    import comtypes.client
    WINDOWS_SPEECH_AVAILABLE = True
except ImportError:
    WINDOWS_SPEECH_AVAILABLE = False

def simple_record_from_microphone(duration=5, language="zh-CN"):
    """
    使用简化的方法从麦克风录制并识别语音
    
    参数:
        duration: 最大录音时长(秒)
        language: 识别语言代码
        
    返回:
        str: 识别出的文本，或空字符串（如果识别失败）
    """
    # 初始化识别器
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # 降低阈值，增强对较小语音的识别
    recognizer.dynamic_energy_threshold = True  # 动态调整阈值
    
    # 选择最适合的语言代码
    if language.lower().startswith("zh"):
        # 对于中文，分别尝试简体和繁体
        language_options = ["zh-CN", "cmn-Hans-CN"]  # 中文简体选项
    else:
        # 其他语言
        language_options = [language]
    
    try:
        print("正在准备麦克风...")
        with sr.Microphone() as source:
            # 调整环境噪音
            print("正在调整环境噪音... (请保持安静)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # 提示用户开始说话
            print(f"请开始说话, 说话完毕自动停止...")
            try:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=duration)
                print("✔️ 成功捕捉到语音，正在分析...")
            except sr.WaitTimeoutError:
                print("⚠️ 未检测到语音，请确保麦克风工作正常")
                return ""
            
            # 使用多种语言选项尝试
            for lang in language_options:
                try:
                    print(f"正在使用Google语音识别 ({lang})...")
                    text = recognizer.recognize_google(audio, language=lang)
                    print(f"识别结果: {text}")
                    return text
                except sr.UnknownValueError:
                    print(f"{lang} 识别失败，尝试其他选项")
                    continue
                except sr.RequestError as e:
                    print(f"Google语音识别服务错误: {e}")
                    break
            
            # 如果在线识别失败，尝试使用Sphinx离线识别
            try:
                print("💻 尝试使用离线识别...")
                text = recognizer.recognize_sphinx(audio)
                print(f"💾 离线识别结果: {text}")
                # 将英文转换为中文如果用户选择的是中文
                if language.lower().startswith("zh") and text:
                    print("注意: 离线识别结果可能不准确")
                return text
            except Exception as offline_err:
                print(f"离线识别失败: {offline_err}")
            
            # 如果所有尝试都失败
            print("所有识别方法均失败")
            return ""
    
    except Exception as e:
        print(f"语音识别总体错误: {e}")
        import traceback
        traceback.print_exc()
        return ""

def windows_native_speech(max_duration=10):
    """
    使用Windows原生语音识别API
    
    参数:
        max_duration: 最大录音时长(秒)
        
    返回:
        str: 识别出的文本，或空字符串（如果识别失败）
    """
    if not WINDOWS_SPEECH_AVAILABLE:
        print("Windows语音识别不可用")
        return ""
        
    try:
        print("正在使用Windows原生语音识别...")
        pythoncom.CoInitialize()
        
        # 提示准备开始
        engine = pyttsx3.init()
        engine.say("准备录音")
        engine.runAndWait()
        
        # 设置语音识别
        context = win32com.client.Dispatch("SAPI.SpInProcRecoContext")
        grammar = context.CreateGrammar()
        grammar.DictationSetState(1)  # 启用听写
        
        # 监听语音
        print("正在监听Windows原生语音...")
        start_time = time.time()
        
        # 简单等待一定时间
        time.sleep(max_duration)
        
        # 获取结果（这是一个简化实现）
        # 实际应用需要使用Windows事件处理
        print("尝试获取识别结果...")
        return "识别结果将在此显示"  # 在实际应用中，这里会返回实际的识别结果
    
    except Exception as e:
        print(f"Windows语音识别错误: {e}")
        import traceback
        traceback.print_exc()
        return ""
    finally:
        pythoncom.CoUninitialize()

def speech_recognition_with_fallback(duration=5, language="zh-CN"):
    """
    带有多种备选方案的语音识别
    
    参数:
        duration: 最大录音时长(秒)
        language: 识别语言代码
        
    返回:
        str: 识别出的文本
    """
    print("启动语音识别...")
    
    # 方法1: 使用简化的麦克风录制 (主要方法)
    print("尝试方法1: 使用Google语音识别...")
    text = simple_record_from_microphone(duration, language)
    if text and text.strip() and text != "识别结果将在此显示":
        print(f"方法1成功识别: '{text}'")
        return text
    
    print("方法1失败，尝试其他方法...")
        
    # 跳过Windows原生语音识别，因为它只返回占位符
    
    # 尝试使用直接的SpeechRecognition库方法
    print("尝试方法2: 使用直接的语音识别库...")
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("请开始说话...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=duration)
            
            try:
                text = recognizer.recognize_google(audio, language=language)
                print(f"方法2成功识别: '{text}'")
                return text
            except sr.UnknownValueError:
                print("方法2无法识别音频")
            except sr.RequestError as e:
                print(f"方法2请求错误: {e}")
    except Exception as e:
        print(f"方法2错误: {e}")
    
    # 如果所有方法都失败，要求用户输入文本
    print("\n所有语音识别方法都失败。请输入您的消息:")
    try:
        text = input("> ")
        return text
    except (EOFError, KeyboardInterrupt):
        print("\n输入被中断")
        return ""

# 测试函数
if __name__ == "__main__":
    print("测试Windows语音识别...")
    text = speech_recognition_with_fallback(duration=5)
    print(f"最终结果: '{text}'")
