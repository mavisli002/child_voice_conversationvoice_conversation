"""
语音对话助手 - GUI版
---------------------
提供类似ChatGPT的交互体验，支持语音输入和输出。
"""
import os
import sys
import time
import threading
import pathlib
import pygame
import customtkinter as ctk
from datetime import datetime
from dotenv import load_dotenv

# 导入语音助手模块
from voice_assistant.speech_handler import record_and_transcribe
from voice_assistant.text_to_speech import synthesize_speech
from voice_assistant.ai_service import generate_response

# 设置主题
ctk.set_appearance_mode("System")  # 使用系统主题
ctk.set_default_color_theme("blue")  # 蓝色主题

# 加载环境变量
load_dotenv()

# 创建数据目录
data_dir = pathlib.Path("data")
data_dir.mkdir(exist_ok=True)

# 初始化pygame混音器（用于音频播放）
pygame.mixer.init()

class ScrollableTextFrame(ctk.CTkScrollableFrame):
    """可滚动的消息显示框架"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.messages = []
        self.message_widgets = []
        
    def add_message(self, message, is_user=False):
        """添加一条消息到聊天记录"""
        # 创建消息框架
        msg_frame = ctk.CTkFrame(self, fg_color="transparent")
        msg_frame.pack(fill="x", padx=5, pady=5, anchor="e" if is_user else "w")
        
        # 设置消息气泡的颜色
        if is_user:
            bubble_color = "#2986CC"  # 用户消息使用蓝色
            text_color = "white"
            anchor = "e"
        else:
            bubble_color = "#343541"  # AI消息使用深灰色
            text_color = "white"
            anchor = "w"
        
        # 创建消息气泡
        bubble = ctk.CTkFrame(msg_frame, fg_color=bubble_color, corner_radius=15)
        bubble.pack(padx=10, pady=5, anchor=anchor)
        
        # 添加消息文本
        message_text = ctk.CTkLabel(
            bubble,
            text=message,
            wraplength=500,
            justify="left",
            text_color=text_color,
            padx=10,
            pady=10
        )
        message_text.pack()
        
        # 保存消息内容和控件
        self.messages.append(message)
        self.message_widgets.append(msg_frame)
        
        # 滚动到最新消息
        self.after(100, self._scroll_to_bottom)
        
    def _scroll_to_bottom(self):
        """滚动到聊天记录底部"""
        self._parent_canvas.yview_moveto(1.0)
        
    def clear_messages(self):
        """清空所有消息"""
        for widget in self.message_widgets:
            widget.destroy()
        self.messages = []
        self.message_widgets = []


class VoiceChatApp(ctk.CTk):
    """语音对话助手GUI应用"""
    def __init__(self):
        super().__init__()
        
        # 应用程序设置
        self.title("语音对话助手")
        self.geometry("800x650")
        self.minsize(700, 500)
        
        # 状态变量
        self.is_recording = False
        self.is_processing = False
        self.is_playing = False
        self.count = 0
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题。"}]
        
        # 创建界面
        self.create_widgets()
        
        # 显示欢迎消息
        self.show_welcome_message()
    
    def create_widgets(self):
        """创建GUI组件"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 主界面容器
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        
        # 对话记录显示区域
        self.chat_frame = ScrollableTextFrame(main_frame)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 底部控制区域
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # 消息输入框
        input_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.message_input = ctk.CTkTextbox(input_frame, height=70, corner_radius=10)
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.message_input.bind("<Return>", self.on_enter_pressed)
        
        # 功能按钮区域
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="w", pady=5)
        
        # 麦克风按钮
        self.mic_button = ctk.CTkButton(
            button_frame,
            text="🎤 语音输入",
            command=self.toggle_recording,
            width=120,
            height=35
        )
        self.mic_button.grid(row=0, column=0, padx=5)
        
        # 发送按钮
        self.send_button = ctk.CTkButton(
            button_frame,
            text="发送",
            command=self.send_message,
            width=120,
            height=35
        )
        self.send_button.grid(row=0, column=1, padx=5)
        
        # 清空按钮
        clear_button = ctk.CTkButton(
            button_frame,
            text="清空对话",
            command=self.clear_chat,
            width=120,
            height=35,
            fg_color="#555555"
        )
        clear_button.grid(row=0, column=2, padx=5)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(button_frame, text="就绪", width=200)
        self.status_label.grid(row=0, column=3, padx=20)
    
    def show_welcome_message(self):
        """显示欢迎消息"""
        welcome_message = "欢迎使用语音对话助手！\n您可以通过语音或文字与我交流。\n点击左下角的麦克风按钮开始语音输入，或直接在文本框中输入文字后按回车发送。"
        self.chat_frame.add_message(welcome_message, is_user=False)
    
    def set_status(self, text):
        """更新状态标签"""
        self.status_label.configure(text=text)
    
    def toggle_recording(self):
        """切换录音状态"""
        if self.is_recording:
            # 停止录音
            self.is_recording = False
            self.mic_button.configure(text="🎤 语音输入")
            return
            
        if self.is_processing:
            return
            
        # 开始录音
        self.is_recording = True
        self.mic_button.configure(text="⏹ 停止录音")
        self.set_status("正在录音...")
        
        # 在后台线程中处理录音
        threading.Thread(target=self.record_audio, daemon=True).start()
    
    def record_audio(self):
        """录制并识别语音"""
        try:
            user_text = record_and_transcribe(duration=10, language="zh-CN")
            self.is_recording = False
            
            # 在主线程中更新UI
            self.after(0, lambda: self.mic_button.configure(text="🎤 语音输入"))
            
            if user_text:
                # 设置输入框文本
                self.after(0, lambda: self.message_input.delete("0.0", "end"))
                self.after(0, lambda: self.message_input.insert("0.0", user_text))
                self.after(0, lambda: self.set_status("已识别语音，可以发送"))
            else:
                self.after(0, lambda: self.set_status("无法识别语音，请重试"))
        except Exception as e:
            self.is_recording = False
            self.after(0, lambda: self.mic_button.configure(text="🎤 语音输入"))
            self.after(0, lambda: self.set_status(f"录音出错: {e}"))
    
    def on_enter_pressed(self, event):
        """处理回车键按下事件"""
        # 按下Shift+Enter时插入换行符
        if event.state & 0x1:  # Shift键被按下
            return
        # 普通Enter发送消息
        self.send_message()
        return "break"  # 阻止默认的换行行为
    
    def send_message(self):
        """发送用户消息并获取AI回复"""
        if self.is_processing:
            return
            
        # 获取用户输入
        user_text = self.message_input.get("0.0", "end").strip()
        if not user_text:
            return
            
        # 清空输入框
        self.message_input.delete("0.0", "end")
        
        # 显示用户消息
        self.chat_frame.add_message(user_text, is_user=True)
        
        # 标记正在处理
        self.is_processing = True
        self.set_status("AI正在思考...")
        self.count += 1
        
        # 在后台处理AI响应
        threading.Thread(target=self.get_ai_response, args=(user_text,), daemon=True).start()
    
    def get_ai_response(self, user_text):
        """获取AI响应并显示"""
        try:
            # 添加用户消息到历史
            self.messages.append({"role": "user", "content": user_text})
            
            # 获取AI回复
            ai_response = generate_response(self.messages)
            
            # 添加AI回复到历史
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # 在主线程中更新UI
            self.after(0, lambda: self.chat_frame.add_message(ai_response, is_user=False))
            self.after(0, lambda: self.set_status("生成语音回复中..."))
            
            # 转换为语音
            mp3_filename = f"response_{self.count}.mp3"
            synthesize_speech(ai_response, mp3_filename)
            
            # 播放语音
            self.play_audio(mp3_filename)
            
        except Exception as e:
            self.after(0, lambda: self.set_status(f"处理出错: {e}"))
        finally:
            self.is_processing = False
    
    def play_audio(self, mp3_filename):
        """播放生成的语音"""
        try:
            # 获取音频文件完整路径
            audio_path = str(pathlib.Path("data") / mp3_filename)
            
            # 确保文件存在
            if not os.path.exists(audio_path):
                self.after(0, lambda: self.set_status(f"无法找到音频文件"))
                return
                
            self.after(0, lambda: self.set_status("正在播放语音..."))
            
            # 停止任何当前播放的音频
            pygame.mixer.music.stop()
            
            # 加载并播放音频文件
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # 等待音频播放完成
            self.is_playing = True
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            self.is_playing = False
            
            self.after(0, lambda: self.set_status("就绪"))
        except Exception as e:
            self.after(0, lambda: self.set_status(f"播放音频出错: {e}"))
            self.is_playing = False
    
    def clear_chat(self):
        """清空对话记录"""
        self.chat_frame.clear_messages()
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题。"}]
        self.count = 0
        self.show_welcome_message()
        self.set_status("对话已清空")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        # 停止任何播放中的音频
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        # 保存对话记录
        self.save_conversation()
        # 关闭窗口
        self.destroy()
    
    def save_conversation(self):
        """保存对话记录"""
        if len(self.messages) <= 1:
            return
            
        try:
            # 创建保存文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"
            file_path = data_dir / filename
            
            # 保存对话内容
            with open(file_path, "w", encoding="utf-8") as f:
                for message in self.messages:
                    if message["role"] == "system":
                        continue
                    role = "用户" if message["role"] == "user" else "助手"
                    f.write(f"{role}: {message['content']}\n\n")
        except Exception as e:
            print(f"保存对话记录时出错: {e}")


# 创建打包函数
def create_exe():
    """创建可执行文件的辅助函数"""
    import PyInstaller.__main__
    
    PyInstaller.__main__.run([
        'voice_chat_gui.py',
        '--onefile',
        '--windowed',
        '--name=语音对话助手',
        '--icon=app_icon.ico',
        '--add-data=voice_assistant;voice_assistant',
    ])


if __name__ == "__main__":
    try:
        app = VoiceChatApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
