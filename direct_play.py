"""
简化版语音对话助手 - 直接播放版
----------------------------------
专注于核心功能：
1. 语音/文本输入
2. AI处理
3. 直接语音输出（无需外部播放器）
"""
import os
import sys
import time
import pathlib
import pygame
import platform
from dotenv import load_dotenv

# 导入语音助手模块
from voice_assistant.real_speech_to_text import record_and_transcribe
from voice_assistant.text_to_speech import synthesize_speech
from voice_assistant.ai_service import generate_response

# 加载环境变量
load_dotenv()

# 创建数据目录
data_dir = pathlib.Path("data")
data_dir.mkdir(exist_ok=True)

# 初始化pygame音频
pygame.mixer.init()
print("音频系统初始化完成")

def direct_play(audio_path):
    """直接播放音频文件，不使用外部播放器"""
    try:
        print(f"正在播放语音回复...")
        
        # 确保文件存在
        if not os.path.exists(audio_path):
            print(f"错误: 无法找到音频文件: {audio_path}")
            return False
            
        # 停止任何正在播放的音频
        pygame.mixer.music.stop()
        
        # 加载并播放音频文件
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        # 等待音频播放完成
        print("播放中...", end="", flush=True)
        while pygame.mixer.music.get_busy():
            print(".", end="", flush=True)
            time.sleep(0.5)
            
        print("\n语音播放完成")
        return True
    except Exception as e:
        print(f"播放音频时出错: {e}")
        return False

def voice_chat_loop():
    """简单的语音对话循环"""
    # 初始化对话历史
    messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题。"}]
    count = 0
    exit_phrases = {"exit", "quit", "bye", "结束", "退出", "拜拜", "再见"}
    
    print("\n===== 语音对话助手 (直接播放版) =====")
    print("- 说出或输入您的消息")
    print("- 语音回复将直接在窗口中播放")
    print("- 输入'exit'或'退出'结束对话")
    print("=====================================\n")
    
    running = True
    while running:
        count += 1
        print(f"\n[对话 #{count}]")
        
        # 尝试语音输入
        try:
            print("正在倾听... (请现在开始说话)")
            user_text = record_and_transcribe(duration=5, language="zh-CN")
            
            # 如果语音识别失败，回退到文本输入
            if not user_text:
                print("无法识别语音。请输入您的消息:")
                user_text = input("> ")
        except Exception as e:
            print(f"语音输入出错: {e}")
            try:
                print("请输入您的消息:")
                user_text = input("> ")
            except (EOFError, KeyboardInterrupt):
                print("\n用户终止，退出对话")
                break
            
        # 检查是否为空
        if not user_text:
            print("未检测到输入，请重试")
            continue
            
        print(f"\n用户: {user_text}")
        
        # 检查退出命令
        if any(phrase in user_text.lower() for phrase in exit_phrases):
            print("检测到退出指令，结束对话")
            running = False
            break
            
        # 发送到AI并获取回复
        messages.append({"role": "user", "content": user_text})
        print("正在处理您的请求...")
        ai_response = generate_response(messages)
        print(f"\n助手: {ai_response}")
        messages.append({"role": "assistant", "content": ai_response})
        
        # 转换为语音并直接播放
        print("正在生成语音回复...")
        audio_file = f"response_{count}.mp3"
        success = synthesize_speech(ai_response, audio_file)
        
        if success:
            # 直接在当前窗口播放音频
            audio_path = str(data_dir / audio_file)
            direct_play(audio_path)
        else:
            print("语音生成失败，无法播放")
        
        print("\n" + "-" * 50)

# 主程序入口
if __name__ == "__main__":
    try:
        # 设置命令行编码（用于Windows）
        if platform.system() == "Windows":
            os.system("chcp 65001 >nul 2>&1")
            
        voice_chat_loop()
    except KeyboardInterrupt:
        print("\n程序被用户终止")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n语音对话助手已关闭，再见！")
        # 确保pygame正确关闭
        pygame.mixer.quit()
