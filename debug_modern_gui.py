#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试版的现代语音对话助手GUI
用于捕获详细的错误信息
"""
import os
import sys
import io
import time
import pathlib
import threading
import datetime
import traceback

# 设置详细的错误日志
def setup_error_logging():
    # 确保日志目录存在
    log_dir = pathlib.Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志文件
    log_file = log_dir / f"error_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # 重定向标准错误输出到文件
    sys.stderr = open(log_file, 'w', encoding='utf-8')
    
    return log_file

def run_with_error_catching():
    log_file = setup_error_logging()
    
    try:
        print(f"启动调试版GUI，错误日志将保存到: {log_file}")
        
        # 尝试导入必要的模块
        try:
            print("导入customtkinter...")
            import customtkinter as ctk
            from PIL import Image, ImageTk
            print("导入成功!")
        except ImportError as e:
            print(f"导入错误: {e}")
            print("尝试安装缺失的包...")
            import subprocess
            subprocess.call([sys.executable, "-m", "pip", "install", "customtkinter", "pillow"])
            import customtkinter as ctk
            from PIL import Image, ImageTk
        
        # 导入语音助手模块
        print("导入语音助手模块...")
        from voice_assistant.windows_speech import windows_record_and_transcribe
        from voice_assistant.text_to_speech import synthesize_speech
        from voice_assistant.ai_service import generate_response
        from voice_assistant.audio_player import play_audio, stop_audio
        print("语音助手模块导入成功!")
        
        # 导入主程序
        print("导入ModernVoiceAssistantApp...")
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from modern_gui import ModernVoiceAssistantApp
        print("ModernVoiceAssistantApp导入成功!")
        
        # 启动应用
        print("创建应用实例...")
        app = ModernVoiceAssistantApp()
        print("启动应用主循环...")
        app.mainloop()
        
    except Exception as e:
        print(f"发生严重错误: {e}")
        traceback.print_exc(file=sys.stderr)
        traceback.print_exc()
        
        # 尝试显示错误对话框
        try:
            from tkinter import messagebox
            messagebox.showerror("启动错误", 
                                f"启动应用时发生错误:\n\n{e}\n\n详细错误日志已保存到: {log_file}")
        except:
            print("无法显示错误对话框")
            
        # 保持控制台窗口打开
        input("按Enter键退出...")

if __name__ == "__main__":
    run_with_error_catching()
