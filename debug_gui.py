#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI调试程序
"""
import sys
import traceback

def main():
    try:
        print("开始调试GUI程序...")
        
        # 步骤1: 导入基础库
        print("步骤1: 导入基础库")
        import os
        import time
        import pathlib
        import threading
        from PIL import Image, ImageTk
        print("基础库导入成功")
        
        # 步骤2: 导入customtkinter
        print("步骤2: 导入customtkinter")
        import customtkinter as ctk
        print("customtkinter导入成功")
        
        # 步骤3: 导入语音处理模块
        print("步骤3: 导入语音处理模块")
        import platform
        if platform.system() == 'Windows':
            from voice_assistant.windows_speech import windows_record_and_transcribe
            print("Windows语音模块导入成功")
        else:
            from voice_assistant.real_speech_to_text import record_and_transcribe
            print("标准语音模块导入成功")
            
        from voice_assistant.text_to_speech import synthesize_speech
        from voice_assistant.ai_service import generate_response
        print("所有语音处理模块导入成功")
        
        # 步骤4: 创建必要目录
        print("步骤4: 创建必要目录")
        data_dir = pathlib.Path("data")
        data_dir.mkdir(exist_ok=True)
        resources_dir = pathlib.Path("data/resources")
        resources_dir.mkdir(exist_ok=True)
        print("必要目录创建完成")
        
        # 步骤5: 从GUI文件导入主类
        print("步骤5: 从GUI文件导入主类")
        from chatgpt_style_gui import ChatGPTWindow
        print("GUI主类导入成功")
        
        # 步骤6: 初始化GUI
        print("步骤6: 初始化GUI")
        app = ChatGPTWindow()
        print("GUI初始化成功")
        
        # 步骤7: 运行GUI主循环
        print("步骤7: 运行GUI主循环")
        app.mainloop()
        
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
