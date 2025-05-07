#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
极简语音对话助手GUI
专为解决Windows系统闪退问题
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import pathlib

# 确保数据目录存在
os.makedirs("data/resources", exist_ok=True)

class SimpleVoiceAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("语音对话助手")
        self.geometry("800x600")
        
        # 设置中文字体
        self.default_font = ("Microsoft YaHei UI", 10)
        
        # 配置主窗口
        self.configure(bg="#2b2b2b")
        self.minsize(700, 500)
        
        # 创建主框架
        self.main_frame = tk.Frame(self, bg="#2b2b2b")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        self.title_label = tk.Label(
            self.main_frame, 
            text="语音对话助手", 
            font=("Microsoft YaHei UI", 16, "bold"),
            bg="#2b2b2b",
            fg="white"
        )
        self.title_label.pack(pady=(0, 20))
        
        # 对话区域
        self.chat_frame = tk.Frame(self.main_frame, bg="#2b2b2b")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            font=self.default_font,
            bg="#3b3b3b",
            fg="white",
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # 输入区域
        self.input_frame = tk.Frame(self.main_frame, bg="#2b2b2b")
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.text_input = tk.Text(
            self.input_frame,
            height=3,
            font=self.default_font,
            bg="#3b3b3b",
            fg="white",
            wrap=tk.WORD,
            padx=10,
            pady=5
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self.on_send)
        
        # 按钮样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=self.default_font)
        
        # 发送按钮
        self.send_button = ttk.Button(
            self.input_frame,
            text="发送",
            command=self.on_send
        )
        self.send_button.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_bar = tk.Label(
            self,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Microsoft YaHei UI", 9),
            bg="#222222",
            fg="white"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加欢迎消息
        self.append_to_chat("系统", "欢迎使用语音对话助手！\n输入文字或问题，按回车键发送。")
    
    def set_status(self, text):
        """更新状态栏"""
        self.status_bar.config(text=text)
        self.update_idletasks()
    
    def append_to_chat(self, speaker, message):
        """添加消息到聊天区域"""
        self.chat_display.config(state=tk.NORMAL)
        
        # 添加时间戳
        timestamp = time.strftime("%H:%M:%S")
        
        # 根据说话者格式化消息
        if speaker == "用户":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 你: ", "user")
            self.chat_display.tag_configure("user", foreground="#4a9eff", font=(self.default_font[0], self.default_font[1], "bold"))
        elif speaker == "助手":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 助手: ", "assistant")
            self.chat_display.tag_configure("assistant", foreground="#10a37f", font=(self.default_font[0], self.default_font[1], "bold"))
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] {speaker}: ", "system")
            self.chat_display.tag_configure("system", foreground="#ff7043", font=(self.default_font[0], self.default_font[1], "bold"))
        
        # 添加消息内容
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def on_send(self, event=None):
        """处理发送消息"""
        user_text = self.text_input.get("1.0", tk.END).strip()
        
        if not user_text:
            return "break"
        
        # 清空输入框
        self.text_input.delete("1.0", tk.END)
        
        # 显示用户消息
        self.append_to_chat("用户", user_text)
        
        # 设置状态
        self.set_status("正在处理...")
        
        # 模拟AI响应
        def respond():
            # 模拟思考时间
            time.sleep(1)
            
            # 根据用户输入生成简单回复
            if "你好" in user_text or "问好" in user_text:
                response = "你好！我是您的语音助手，有什么可以帮助您的？"
            elif "退出" in user_text or "结束" in user_text or "exit" in user_text.lower():
                response = "再见！期待下次与您交流。"
                # 延迟关闭
                self.after(2000, self.destroy)
            else:
                # 默认回复
                response = "我收到了您的消息，但在这个简化版本中，我只能提供基本回复。请使用完整版获取更好的体验。"
            
            # 显示助手回复
            self.after(0, lambda: self.append_to_chat("助手", response))
            self.after(0, lambda: self.set_status("就绪"))
        
        # 在后台线程中处理
        response_thread = threading.Thread(target=respond)
        response_thread.daemon = True
        response_thread.start()
        
        return "break"  # 阻止在文本框中插入回车符

if __name__ == "__main__":
    try:
        app = SimpleVoiceAssistantApp()
        app.mainloop()
    except Exception as e:
        # 显示错误对话框
        try:
            messagebox.showerror("启动错误", f"程序启动时发生错误: {str(e)}")
        except:
            print(f"程序启动时发生错误: {e}")
            import traceback
            traceback.print_exc()
