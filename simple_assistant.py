"""
简易对话助手 - 专注于文本交互和语音回复
----------------------------
移除复杂的语音识别，专注于：
1. 简洁美观的橘色界面
2. 文本输入方式
3. 语音播放功能
"""
import os
import sys
import time
import threading
import pathlib
import pygame
import customtkinter as ctk
from dotenv import load_dotenv
import pyttsx3  # 作为语音合成的备选方案
import speech_recognition as sr  # 直接导入语音识别库

# 导入AI服务模块
from voice_assistant.ai_service import generate_response

# 设置主题
ctk.set_appearance_mode("Light")  # 使用浅色主题
ctk.set_default_color_theme("blue")  # 基础主题，我们会覆盖颜色

# 儿童友好的颜色方案 - 浅橙色系
KIDS_COLORS = {
    "bg_main": "#FFF4E6",        # 主背景 - 浅橙黄色
    "bg_secondary": "#FFDAB9",   # 次要背景 - 浅桃色
    "accent": "#FF9966",         # 强调色 - 橙色
    "accent_hover": "#FF7F50",   # 强调色悬停 - 珊瑚色
    "user_msg": "#FFE4C4",       # 用户消息 - 浅杨色
    "bot_msg": "#FFDAB9",        # AI消息 - 浅桃色
    "text": "#664433",           # 文本 - 深棕色
    "placeholder": "#AA8866",    # 占位符文本 - 中棕色
    "border": "#FFCC99",         # 边框 - 橙黄色
    "error": "#FF6666",          # 错误 - 浅红色
    
    # 儿童友好的颜色
    "mic_button": "#FF7043",     # 录音按钮 - 深橙色
    "send_button": "#66BB6A",    # 发送按钮 - 浅绿色
    "mic_hover": "#E64A19",      # 录音按钮悬停 - 红橙色
    "send_hover": "#43A047"      # 发送按钮悬停 - 绿色
}

# 加载环境变量
load_dotenv()

# 创建数据目录
data_dir = pathlib.Path("data")
data_dir.mkdir(exist_ok=True)

# 初始化pygame混音器（用于音频播放）
pygame.mixer.init()


class RoundedMessageFrame(ctk.CTkFrame):
    """圆角消息框组件"""
    def __init__(self, master, message, is_user=False, **kwargs):
        # 设置背景色
        bg_color = KIDS_COLORS["user_msg"] if is_user else KIDS_COLORS["bot_msg"]
        super().__init__(
            master, 
            fg_color=bg_color, 
            corner_radius=15,
            border_width=1,
            border_color=KIDS_COLORS["border"],
            **kwargs
        )
        
        self.grid_columnconfigure(1, weight=1)
        
        # 内容容器
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        
        # 头像 - 使用更卡通化的图标
        avatar_size = 36
        avatar_frame = ctk.CTkFrame(
            content_frame, 
            width=avatar_size, 
            height=avatar_size,
            fg_color=KIDS_COLORS["accent"] if is_user else "#FFB6C1",  # 浅粉色机器人
            corner_radius=avatar_size//2
        )
        avatar_frame.grid(row=0, column=0, padx=(0, 15), sticky="n")
        avatar_frame.grid_propagate(False)
        
        # 使用可爱的表情符号作为头像
        avatar_text = "U" if is_user else "AI"
        avatar_label = ctk.CTkLabel(
            avatar_frame, 
            text=avatar_text,
            text_color="white",
            font=("Arial", 16, "bold")
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 消息文本 - 使用更大、更圆润的字体
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            wraplength=700,
            justify="left",
            text_color=KIDS_COLORS["text"],
            anchor="w",
            font=("Comic Sans MS", 14)  # 更友好的字体
        )
        message_label.grid(row=0, column=1, sticky="w")


class SimpleAssistant(ctk.CTk):
    """简易对话助手"""
    def __init__(self):
        super().__init__()
        
        # 应用程序设置
        self.title("简易对话助手")
        self.geometry("900x700")
        self.minsize(700, 500)
        
        # 状态变量
        self.is_processing = False
        self.count = 0
        self.messages = [{"role": "system", "content": "你是一个友好的助手，请使用简单友好的语言。"}]
        
        # 设置TTS引擎
        self.setup_tts_engine()
        
        # 创建界面
        self.create_widgets()
        
        # 显示欢迎消息
        self.add_bot_message("你好！我是你的对话助手。请在下方输入框中输入你想说的话，我会用语音回复你。")
    
    def setup_tts_engine(self):
        """设置文字转语音引擎"""
        self.tts_engine = pyttsx3.init()
        # 设置语速和声音
        self.tts_engine.setProperty('rate', 150)  # 语速适中
        # 选择女声
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "chinese" in voice.id.lower() or "mandarin" in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
    
    def create_widgets(self):
        """创建GUI组件"""
        # 配置整体布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 主界面容器 - 浅橘色背景
        self.main_frame = ctk.CTkFrame(self, fg_color=KIDS_COLORS["bg_main"])
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 聊天区域 - 滚动容器
        self.chat_container = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color=KIDS_COLORS["bg_main"],
            scrollbar_button_color=KIDS_COLORS["accent"],
            scrollbar_button_hover_color=KIDS_COLORS["accent_hover"]
        )
        self.chat_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 90))
        
        # 设置底部输入区域容器
        self.input_frame = ctk.CTkFrame(
            self.main_frame, 
            height=70, 
            fg_color=KIDS_COLORS["bg_secondary"],
            corner_radius=20,
            border_width=2,
            border_color=KIDS_COLORS["border"]
        )
        self.input_frame.grid(row=2, column=0, sticky="sew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)
        
        # 输入框容器 - 使用中心对齐
        input_area = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_area.place(relx=0.5, rely=0.5, relwidth=0.95, anchor="center")
        input_area.grid_columnconfigure(1, weight=1)
        
        # 设置按钮高度
        button_height = 28  # 按用户要求调整为28px
        
        # 录音按钮 - 添加背景色
        self.mic_button = ctk.CTkButton(
            input_area,
            text="🎤",  # 麦克风图标
            width=50,  # 保持增大的宽度
            height=36,  # 保持增大的高度
            corner_radius=18,  # 保持圆滑边角
            fg_color=KIDS_COLORS["mic_button"],  # 添加背景色
            hover_color=KIDS_COLORS["mic_hover"],  # 使用对应的悬停颜色
            font=("Arial", 24, "bold"),  # 保持大图标
            text_color="white",  # 文字改回白色
            border_width=0,  # 保持无边框
            command=self.start_recording
        )
        self.mic_button.grid(row=0, column=0, padx=(0, 10), sticky="ns")  # 添加ns粘性使其垂直居中
        
        # 录音状态变量
        self.is_recording = False
        
        # 文本输入框 - 降低高度
        self.message_input = ctk.CTkTextbox(
            input_area,
            height=30,
            fg_color="white",
            border_color=KIDS_COLORS["border"],
            border_width=2,
            corner_radius=15,
            text_color=KIDS_COLORS["text"]
        )
        self.message_input.grid(row=0, column=1, sticky="nsew")  # 添加ns使其垂直居中
        self.message_input.bind("<Return>", self.on_enter_pressed)
        
        # 设置占位符文字
        self.message_input.insert("0.0", "在这里输入你想说的话...")
        self.message_input.bind("<FocusIn>", self.clear_placeholder)
        self.message_input.bind("<FocusOut>", self.add_placeholder)
        
        # 发送按钮 - 添加背景色
        self.send_button = ctk.CTkButton(
            input_area,
            text="🛬",  # 纸飞机图标
            width=50,  # 保持增大的宽度
            height=36,  # 保持增大的高度
            corner_radius=18,  # 保持圆滑边角
            fg_color=KIDS_COLORS["send_button"],  # 添加背景色
            hover_color=KIDS_COLORS["send_hover"],  # 使用对应的悬停颜色
            font=("Arial", 24, "bold"),  # 保持大图标
            text_color="white",  # 文字改回白色
            border_width=0,  # 保持无边框
            command=self.send_message
        )
        self.send_button.grid(row=0, column=2, padx=(15, 0), sticky="ens")  # 添加ns使其垂直居中
        
        # 状态指示器
        self.status_frame = ctk.CTkFrame(
            self.main_frame, 
            height=30, 
            fg_color=KIDS_COLORS["bg_secondary"],
            corner_radius=15
        )
        self.status_frame.grid(row=3, column=0, sticky="s", padx=20, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="准备好啦！", 
            text_color=KIDS_COLORS["text"],
            font=("Comic Sans MS", 12),
            padx=15
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 创建"新对话"按钮
        new_chat_button = ctk.CTkButton(
            self.status_frame,
            text="清空对话",
            width=100,
            height=24,
            corner_radius=12,
            fg_color=KIDS_COLORS["accent"],
            hover_color=KIDS_COLORS["accent_hover"],
            text_color="white",
            font=("Comic Sans MS", 12),
            command=self.clear_chat
        )
        new_chat_button.pack(side="right", padx=10, pady=2)
    
    def clear_placeholder(self, event):
        """清除输入框占位符文本"""
        if self.message_input.get("0.0", "end-1c") == "在这里输入你想说的话...":
            self.message_input.delete("0.0", "end")
            self.message_input.configure(text_color=KIDS_COLORS["text"])
    
    def add_placeholder(self, event):
        """添加输入框占位符文本"""
        if not self.message_input.get("0.0", "end-1c"):
            self.message_input.configure(text_color=KIDS_COLORS["placeholder"])
            self.message_input.insert("0.0", "在这里输入你想说的话...")
    
    def add_user_message(self, message):
        """添加用户消息"""
        msg = RoundedMessageFrame(self.chat_container, message, is_user=True)
        msg.pack(fill="x", padx=10, pady=5)
        
        # 滚动到底部
        self.chat_container._parent_canvas.yview_moveto(1.0)
    
    def add_bot_message(self, message):
        """添加机器人消息"""
        msg = RoundedMessageFrame(self.chat_container, message, is_user=False)
        msg.pack(fill="x", padx=10, pady=5)
        
        # 滚动到底部
        self.chat_container._parent_canvas.yview_moveto(1.0)
    
    def set_status(self, text):
        """更新状态标签"""
        self.status_label.configure(text=text)
    
    def start_recording(self):
        """开始语音录制"""
        if self.is_processing or self.is_recording:
            return
            
        self.is_recording = True
        self.set_status("正在录音...请对着麦克风说话")
        self.mic_button.configure(text="停止", fg_color="#FF6666")
        
        # 在后台线程执行录音
        threading.Thread(target=self.perform_recording, daemon=True).start()
    
    def perform_recording(self):
        """执行录音过程"""
        try:
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300  # 降低阈值，对较小声音更敏感
            recognizer.dynamic_energy_threshold = True  # 动态调整阈值
            
            with sr.Microphone() as source:
                # 调整环境噪音
                self.after(0, lambda: self.set_status("正在调整麦克风噪音..."))
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # 录制音频
                self.after(0, lambda: self.set_status("请开始说话，说完后会自动识别"))
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    self.after(0, lambda: self.set_status("录音完成，正在识别..."))
                except sr.WaitTimeoutError:
                    self.after(0, lambda: self.set_status("没有检测到语音，请重试"))
                    self.after(0, lambda: self.reset_recording_button())
                    return
                    
                # 试图识别
                try:
                    user_text = recognizer.recognize_google(audio, language="zh-CN")
                    if user_text:
                        # 在输入框中显示识别到的文本
                        self.after(0, lambda text=user_text: self.set_recognized_text(text))
                except sr.UnknownValueError:
                    self.after(0, lambda: self.set_status("无法识别您的语音，请重试或手动输入"))
                except sr.RequestError:
                    self.after(0, lambda: self.set_status("语音识别服务不可用，请手动输入"))
        except Exception as e:
            self.after(0, lambda: self.set_status(f"录音错误: {str(e)}"))
        finally:
            self.after(0, lambda: self.reset_recording_button())
    
    def reset_recording_button(self):
        """重置录音按钮状态"""
        self.is_recording = False
        self.mic_button.configure(text="录音", fg_color=KIDS_COLORS["accent"])
    
    def set_recognized_text(self, text):
        """设置识别到的文本并自动发送"""
        # 清除占位符文本
        self.message_input.delete("0.0", "end")
        # 设置识别到的文本
        self.message_input.insert("0.0", text)
        self.message_input.configure(text_color=KIDS_COLORS["text"])
        # 更新状态
        self.set_status(f"已识别并自动发送: '{text}'")
        # 等待短暂后自动发送，让用户有时间看到识别结果
        self.after(800, self.send_message)
    
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
        user_text = self.message_input.get("0.0", "end-1c").strip()
        if not user_text or user_text == "在这里输入你想说的话...":
            return
            
        # 清空输入框
        self.message_input.delete("0.0", "end")
        
        # 显示用户消息
        self.add_user_message(user_text)
        
        # 标记正在处理
        self.is_processing = True
        self.set_status("思考中...")
        self.count += 1
        
        # 在后台处理AI响应
        threading.Thread(target=self.get_ai_response, args=(user_text,), daemon=True).start()
    
    def get_ai_response(self, user_text):
        """获取AI响应并显示"""
        try:
            # 添加用户消息到历史
            self.messages.append({"role": "user", "content": user_text})
            
            # 首先显示“思考中”消息
            thinking_message = RoundedMessageFrame(self.chat_container, "正在思考...", is_user=False)
            thinking_message.pack(fill="x", padx=10, pady=5)
            # 滚动到底部
            self.chat_container._parent_canvas.yview_moveto(1.0)
            
            # 获取AI回复
            ai_response = generate_response(self.messages)
            
            # 添加AI回复到历史
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # 移除“思考中”消息并显示真正的回复
            thinking_message.destroy()
            self.after(0, lambda: self.add_bot_message(ai_response))
            self.after(0, lambda: self.set_status("正在生成语音..."))
            
            # 使用pyttsx3直接播放语音
            self.speak_text(ai_response)
            
            # 处理完成
            self.after(0, lambda: self.set_status("准备好啦！"))
            self.is_processing = False
            
        except Exception as e:
            self.after(0, lambda: self.set_status(f"处理出错: {e}"))
            self.is_processing = False
    
    def speak_text(self, text):
        """使用pyttsx3直接播放文本"""
        try:
            self.after(0, lambda: self.set_status("正在说话..."))
            
            # 使用线程来避免界面冻结
            def do_speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.after(0, lambda: self.set_status("准备好啦！"))
            
            # 启动新线程进行语音合成和播放
            threading.Thread(target=do_speak, daemon=True).start()
            
        except Exception as e:
            print(f"语音播放错误: {e}")
            self.after(0, lambda: self.set_status(f"语音播放错误: {e}"))
            # 尝试使用备用方法
            try:
                # 导入文本转语音模块
                from voice_assistant.text_to_speech import synthesize_speech
                # 转换为语音文件
                mp3_filename = f"response_{self.count}.mp3"
                success = synthesize_speech(text, mp3_filename)
                
                if success:
                    # 使用pygame播放
                    self.play_audio_with_pygame(mp3_filename)
                else:
                    self.after(0, lambda: self.set_status("无法生成语音，但你可以阅读回复"))
            except:
                self.after(0, lambda: self.set_status("无法生成语音，但你可以阅读回复"))
    
    def play_audio_with_pygame(self, mp3_filename):
        """使用pygame播放音频文件"""
        try:
            # 获取音频文件完整路径
            audio_path = str(pathlib.Path("data") / mp3_filename)
            
            # 确保文件存在
            if not os.path.exists(audio_path):
                self.after(0, lambda: self.set_status(f"无法找到音频文件"))
                return
                
            self.after(0, lambda: self.set_status("正在播放..."))
            
            # 停止任何当前播放的音频
            pygame.mixer.music.stop()
            
            # 加载并播放音频文件
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # 等待音频播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.after(0, lambda: self.set_status("准备好啦！"))
        except Exception as e:
            self.after(0, lambda: self.set_status(f"播放音频出错: {e}"))
    
    def clear_chat(self):
        """清空对话记录"""
        # 清空聊天容器中的所有控件
        for widget in self.chat_container.winfo_children():
            widget.destroy()
            
        # 重置消息历史
        self.messages = [{"role": "system", "content": "你是一个友好的助手，请使用简单友好的语言。"}]
        self.count = 0
        
        # 显示欢迎消息
        self.add_bot_message("你好！我是你的对话助手。请在下方输入框中输入你想说的话，我会用语音回复你。")
        self.set_status("对话已清空")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        # 停止语音引擎
        try:
            self.tts_engine.stop()
        except:
            pass
            
        # 停止任何播放中的音频
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            
        # 关闭窗口
        self.destroy()


# 主程序
if __name__ == "__main__":
    try:
        app = SimpleAssistant()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
