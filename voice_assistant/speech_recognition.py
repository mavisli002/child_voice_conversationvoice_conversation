"""语音识别模块 - 将语音转换为文本"""
import speech_recognition as sr

def recognize_speech(language="zh-CN", timeout=5):
    """使用麦克风录制语音并转换为文本
    
    参数:
        language: 语言代码 (zh-CN, en-US等)
        timeout: 最大录音时间(秒)
        
    返回:
        str: 识别的文本
    """
    # 创建识别器
    recognizer = sr.Recognizer()
    
    print(f"请说话...(最多 {timeout} 秒)")
    try:
        # 使用麦克风作为音频源
        with sr.Microphone() as source:
            # 调整环境噪音
            print("调整环境噪音...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # 录制音频
            print("开始录音...")
            audio = recognizer.listen(source, timeout=timeout)
            print("录音完成，正在识别...")
            
            # 使用Google语音识别API
            text = recognizer.recognize_google(audio, language=language)
            return text
    except sr.WaitTimeoutError:
        print("没有检测到语音")
        return ""
    except sr.UnknownValueError:
        print("无法识别语音")
        return ""
    except sr.RequestError as e:
        print(f"无法连接到Google语音识别服务: {e}")
        return ""
    except Exception as e:
        print(f"语音识别错误: {e}")
        return ""


def fallback_to_text_input():
    """当语音识别失败时，回退到文本输入"""
    print("请输入您的消息:")
    try:
        return input("> ")
    except (KeyboardInterrupt, EOFError):
        return ""


def get_user_input(language="zh-CN"):
    """获取用户输入，优先使用语音识别，失败时回退到文本输入"""
    # 尝试语音识别
    text = recognize_speech(language=language)
    
    # 如果语音识别失败，回退到文本输入
    if not text:
        print("语音识别失败，请改用键盘输入")
        text = fallback_to_text_input()
        
    return text
