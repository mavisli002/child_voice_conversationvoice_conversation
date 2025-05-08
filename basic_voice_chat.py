#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
极简语音对话助手
专注于核心功能，最小化UI复杂度
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import pathlib

# 确保必要的目录存在
os.makedirs("data", exist_ok=True)

# 导入必要的音频处理模块
try:
    from voice_assistant.audio_player import play_audio, stop_audio
    from voice_assistant.text_to_speech import synthesize_speech
    from voice_assistant.ai_service import generate_response
except ImportError as e:
    print(f"错误: 无法导入基础模块: {e}")
    input("按Enter键退出...")
    sys.exit(1)

class BasicVoiceChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("基础语音助手")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # 设置变量
        self.is_processing = False
        self.conversation_count = 0
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手。"}]
        
        # 创建基础UI
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 聊天区域
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            bg="white",
            height=20
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chat_area.config(state=tk.DISABLED)
        
        # 输入区域
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=10)
        
        self.text_input = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self.on_send)
        
        # 发送按钮
        send_button = ttk.Button(
            input_frame,
            text="发送",
            command=self.on_send
        )
        send_button.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_bar = tk.Label(
            self,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加欢迎消息
        self.add_message("系统", "欢迎使用基础语音助手！请输入文字并按回车发送。")
        
    def set_status(self, status):
        """更新状态栏"""
        self.status_bar.config(text=status)
        
    def add_message(self, sender, message):
        """添加消息到聊天区域"""
        self.chat_area.config(state=tk.NORMAL)
        
        if sender == "用户":
            prefix = "你: "
            tag = "user"
        elif sender == "助手":
            prefix = "助手: "
            tag = "assistant"
        else:
            prefix = f"{sender}: "
            tag = "system"
        
        # 添加消息
        self.chat_area.insert(tk.END, prefix, tag)
        self.chat_area.insert(tk.END, f"{message}\n\n")
        
        # 设置标签样式
        self.chat_area.tag_config("user", foreground="blue")
        self.chat_area.tag_config("assistant", foreground="green")
        self.chat_area.tag_config("system", foreground="red")
        
        # 滚动到底部
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def on_send(self, event=None):
        """处理发送消息"""
        # 获取用户输入
        user_text = self.text_input.get("1.0", tk.END).strip()
        if not user_text or self.is_processing:
            return "break"
        
        # 清空输入框
        self.text_input.delete("1.0", tk.END)
        
        # 显示用户消息
        self.add_message("用户", user_text)
        
        # 添加到对话历史
        self.messages.append({"role": "user", "content": user_text})
        
        # 处理响应
        self.is_processing = True
        self.set_status("处理中...")
        
        # 在后台线程中处理，避免界面冻结
        threading.Thread(target=self.process_response, args=(user_text,), daemon=True).start()
        
        return "break"  # 防止在按回车时换行
    
    def process_response(self, user_text):
        """在后台线程中处理AI响应"""
        try:
            # 生成AI响应
            response = generate_response(self.messages)
            
            # 更新UI(必须在主线程中进行)
            self.after(0, lambda: self.add_message("助手", response))
            
            # 添加到对话历史
            self.messages.append({"role": "assistant", "content": response})
            
            # 生成语音回复
            self.conversation_count += 1
            mp3_filename = f"response_{self.conversation_count}.mp3"
            file_path = pathlib.Path("data") / mp3_filename
            
            # 合成语音
            success = synthesize_speech(response, str(file_path))
            
            if success and os.path.exists(file_path):
                # 播放语音(使用无窗口模式)
                self.after(0, lambda: self.set_status("播放语音中..."))
                
                def on_complete():
                    """语音播放完成后的回调"""
                    self.after(0, lambda: self.set_status("就绪"))
                
                play_audio(str(file_path), callback=on_complete)
            else:
                self.after(0, lambda: self.set_status("语音合成失败"))
        
        except Exception as e:
            self.after(0, lambda: self.set_status(f"错误: {str(e)}"))
            self.after(0, lambda: self.add_message("系统", f"处理消息时出错: {str(e)}"))
        
        finally:
            # 重置处理状态
            self.is_processing = False

if __name__ == "__main__":
    try:
        app = BasicVoiceChat()
        app.mainloop()
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")
