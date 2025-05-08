"""
儿童友好的语音对话助手
----------------------------
特点:
1. 浅橘色主题，适合儿童使用
2. 简洁友好的界面
3. 增强的语音识别和播放功能
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

# 导入语音助手模块
from voice_assistant.speech_handler import record_and_transcribe
from voice_assistant.ai_service import generate_response

# 设置主题
ctk.set_appearance_mode("Light")  # 使用浅色主题
ctk.set_default_color_theme("blue")  # 基础主题，我们会覆盖颜色

# 儿童友好的颜色方案 - 浅橘色系
KIDS_COLORS = {
    "bg_main": "#FFF4E6",        # 主背景 - 浅橘黄色
    "bg_secondary": "#FFDAB9",   # 次要背景 - 浅桃色
    "accent": "#FF9966",         # 强调色 - 橘色
    "accent_hover": "#FF7F50",   # 强调色悬停 - 珊瑚色
    "user_msg": "#FFE4C4",       # 用户消息 - 浅杏色
    "bot_msg": "#FFDAB9",        # AI消息 - 浅桃色
    "text": "#664433",           # 文本 - 深棕色
    "placeholder": "#AA8866",    # 占位符文本 - 中棕色
    "border": "#FFCC99",         # 边框 - 橘黄色
    "error": "#FF6666"           # 错误 - 浅红色
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
        avatar_label = ctk.CTkLabel(
            avatar_frame, 
            text="👧" if is_user else "🤖",  # 使用女孩表情或机器人
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


class KidsVoiceAssistant(ctk.CTk):
    """儿童友好的语音对话助手"""
    def __init__(self):
        super().__init__()
        
        # 应用程序设置
        self.title("小朋友的语音助手")
        self.geometry("900x700")
        self.minsize(700, 500)
        
        # 状态变量
        self.is_recording = False
        self.is_processing = False
        self.count = 0
        self.messages = [{"role": "system", "content": "你是一个友好的助手，专为儿童设计。请使用简单友好的语言。"}]
        
        # 设置TTS引擎
        self.setup_tts_engine()
        
        # 创建界面
        self.create_widgets()
        
        # 显示欢迎消息
        self.add_bot_message("你好啊，小朋友！点击下面的麦克风按钮，跟我说话吧！")
    
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
        
        # 顶部标题栏
        self.title_bar = ctk.CTkFrame(
            self.main_frame, 
            height=60, 
            fg_color=KIDS_COLORS["accent"],
            corner_radius=0
        )
        self.title_bar.grid(row=0, column=0, sticky="ew")
        self.title_bar.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            self.title_bar,
            text="🤖 小朋友的语音助手 🎤",
            font=("Comic Sans MS", 18, "bold"),
            text_color="white"
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 聊天区域 - 滚动容器
        self.chat_container = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color=KIDS_COLORS["bg_main"],
            scrollbar_button_color=KIDS_COLORS["accent"],
            scrollbar_button_hover_color=KIDS_COLORS["accent_hover"]
        )
        self.chat_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(20, 90))
        
        # 设置底部输入区域容器
        self.input_frame = ctk.CTkFrame(
            self.main_frame, 
            height=80, 
            fg_color=KIDS_COLORS["bg_secondary"],
            corner_radius=20,
            border_width=2,
            border_color=KIDS_COLORS["border"]
        )
        self.input_frame.grid(row=2, column=0, sticky="sew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)
        
        # 输入框容器
        input_area = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_area.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        input_area.grid_columnconfigure(1, weight=1)
        
        # 麦克风按钮 - 大一些更容易点击
        self.mic_button = ctk.CTkButton(
            input_area,
            text="🎤",
            width=50,
            height=50,
            corner_radius=25,
            fg_color=KIDS_COLORS["accent"],
            hover_color=KIDS_COLORS["accent_hover"],
            font=("Arial", 18, "bold"),
            command=self.toggle_recording
        )
        self.mic_button.grid(row=0, column=0, padx=(0, 15))
        
        # 文本输入框 - 更圆润的形状
        self.message_input = ctk.CTkTextbox(
            input_area,
            height=50,
            fg_color="white",
            border_color=KIDS_COLORS["border"],
            border_width=2,
            corner_radius=25,
            text_color=KIDS_COLORS["text"]
        )
        self.message_input.grid(row=0, column=1, sticky="ew")
        self.message_input.bind("<Return>", self.on_enter_pressed)
        
        # 设置占位符文字
        self.message_input.insert("0.0", "在这里输入你想说的话...")
        self.message_input.bind("<FocusIn>", self.clear_placeholder)
        self.message_input.bind("<FocusOut>", self.add_placeholder)
        
        # 发送按钮 - 使用纸飞机图标
        self.send_button = ctk.CTkButton(
            input_area,
            text="✈️",
            width=50,
            height=50,
            corner_radius=25,
            fg_color=KIDS_COLORS["accent"],
            hover_color=KIDS_COLORS["accent_hover"],
            font=("Arial", 18, "bold"),
            command=self.send_message
        )
        self.send_button.grid(row=0, column=2, padx=(15, 0))
        
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
            text="🧹 清空对话",
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
    
    def toggle_recording(self):
        """切换录音状态"""
        if self.is_recording:
            # 停止录音
            self.is_recording = False
            self.mic_button.configure(text="🎤", fg_color=KIDS_COLORS["accent"])
            return
            
        if self.is_processing:
            return
            
        # 开始录音
        self.is_recording = True
        self.mic_button.configure(text="⏹", fg_color="#FF6666")  # 红色停止按钮
        self.set_status("正在听你说话...说完了会自动发送")
        
        # 在后台线程中处理录音
        threading.Thread(target=self.record_audio, daemon=True).start()
        
        # 动画效果
        self._update_recording_animation()
    
    def _update_recording_animation(self):
        """更新录音状态动画"""
        if not self.is_recording:
            return
            
        # 闪烁录音按钮
        current_color = self.mic_button.cget("fg_color")
        new_color = "#FF9933" if current_color == "#FF6666" else "#FF6666"
        self.mic_button.configure(fg_color=new_color)
        
        # 每500毫秒更新一次
        self.after(500, self._update_recording_animation)
    
    def record_audio(self):
        """录制并识别语音，完成后自动发送"""
        try:
            # 显示录音提示
            self.after(0, lambda: self.set_status("正在准备听你说话..."))
            
            # 创建临时调试窗口显示语音识别过程
            debug_window = self.create_debug_window()
            
            def add_debug_line(text):
                if debug_window and debug_window.winfo_exists():
                    debug_window.debug_text.configure(state="normal")
                    debug_window.debug_text.insert("end", f"{text}\n")
                    debug_window.debug_text.see("end")
                    debug_window.debug_text.configure(state="disabled")
                    # 更新窗口
                    debug_window.update()
            
            # 修改sys.stdout以捕获print输出
            original_stdout = sys.stdout
            
            class DebugOutput:
                def __init__(self, parent):
                    self.parent = parent
                    
                def write(self, message):
                    original_stdout.write(message)
                    self.parent.after(0, lambda: add_debug_line(message.rstrip()))
                    
                def flush(self):
                    original_stdout.flush()
            
            sys.stdout = DebugOutput(self)
            add_debug_line("===== 开始语音识别 =====")
            add_debug_line(f"系统时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                # 录制并识别语音（简化版本）
                add_debug_line("正在听你说话...")
                
                # 直接使用基础语音识别
                recognizer = sr.Recognizer()
                recognizer.energy_threshold = 300
                recognizer.dynamic_energy_threshold = True
                
                try:
                    with sr.Microphone() as source:
                        add_debug_line("正在调整麦克风恶光噪音...")
                        # 调整噪音
                        recognizer.adjust_for_ambient_noise(source, duration=1)
                        
                        # 录制音频
                        add_debug_line("请开始说话...")
                        try:
                            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                            add_debug_line("录音完成！")
                        except Exception as listen_err:
                            add_debug_line(f"录音错误: {listen_err}")
                            raise
                        
                        # 试图识别
                        add_debug_line("正在识别语音...")
                        try:
                            user_text = recognizer.recognize_google(audio, language="zh-CN")
                            add_debug_line(f"识别成功: '{user_text}'")
                        except sr.UnknownValueError:
                            add_debug_line("识别失败: 无法识别语音")
                            user_text = ""
                        except sr.RequestError as e:
                            add_debug_line(f"请求错误: {e}")
                            user_text = ""
                except Exception as e:
                    add_debug_line(f"录音过程错误: {e}")
                    user_text = ""
            finally:
                # 恢复原始stdout
                sys.stdout = original_stdout
                
            self.is_recording = False
            
            # 重置录音按钮外观
            self.after(0, lambda: self.mic_button.configure(
                text="🎤", 
                fg_color=KIDS_COLORS["accent"]
            ))
            
            if user_text and user_text.strip() and user_text != "识别结果将在此显示":
                # 显示识别到的文本
                self.after(0, lambda: self.set_status(f"我听到了: '{user_text}'"))
                add_debug_line(f"最终识别结果: '{user_text}'")
                
                # 自动发送消息
                self.after(100, lambda: self._send_voice_message(user_text))
            else:
                add_debug_line("❌ 没有听清楚你说的话")
                self.after(0, lambda: self.set_status("没有听清楚，请再说一次或直接输入"))
                
                # 尝试手动输入
                self.prompt_manual_input(debug_window)
        except Exception as e:
            self.is_recording = False
            self.after(0, lambda: self.mic_button.configure(text="🎤", fg_color=KIDS_COLORS["accent"]))
            error_msg = f"录音出错: {str(e)}"
            self.after(0, lambda: self.set_status(error_msg))
            
            import traceback
            error_traceback = traceback.format_exc()
            print(error_traceback)
            
            # 显示错误详情
            self.show_error_dialog("语音识别错误", 
                                   f"错误信息: {str(e)}\n\n详细信息:\n{error_traceback}")
    
    def create_debug_window(self):
        """创建调试窗口"""
        debug_win = ctk.CTkToplevel(self)
        debug_win.title("语音识别调试")
        debug_win.geometry("600x400")
        debug_win.configure(fg_color=KIDS_COLORS["bg_main"])
        debug_win.grab_set()
        
        # 调试文本区域
        debug_win.debug_text = ctk.CTkTextbox(
            debug_win, 
            height=350, 
            width=580,
            fg_color="white",
            text_color=KIDS_COLORS["text"],
            font=("Consolas", 12)
        )
        debug_win.debug_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            debug_win, 
            text="关闭", 
            command=debug_win.destroy,
            fg_color=KIDS_COLORS["accent"],
            hover_color=KIDS_COLORS["accent_hover"],
            corner_radius=15,
            font=("Comic Sans MS", 12)
        )
        close_btn.pack(pady=10)
        
        return debug_win
    
    def prompt_manual_input(self, debug_window=None):
        """提示用户手动输入信息"""
        input_dialog = ctk.CTkInputDialog(
            title="手动输入", 
            text="没听清楚你说的话，请手动输入:"
        )
        text = input_dialog.get_input()
        
        if text and text.strip():
            if debug_window and debug_window.winfo_exists():
                debug_window.debug_text.configure(state="normal")
                debug_window.debug_text.insert("end", f"手动输入: '{text}'\n")
                debug_window.debug_text.configure(state="disabled")
                
            # 发送手动输入的消息
            self._send_voice_message(text)
    
    def show_error_dialog(self, title, message):
        """显示错误对话框"""
        error_window = ctk.CTkToplevel(self)
        error_window.title(title)
        error_window.geometry("600x400")
        error_window.configure(fg_color=KIDS_COLORS["bg_main"])
        error_window.grab_set()
        
        # 错误消息文本区域
        error_text = ctk.CTkTextbox(
            error_window, 
            height=350, 
            width=580,
            fg_color="white",
            text_color=KIDS_COLORS["error"]
        )
        error_text.pack(padx=10, pady=10, fill="both", expand=True)
        error_text.insert("1.0", message)
        error_text.configure(state="disabled")
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            error_window, 
            text="关闭", 
            command=error_window.destroy,
            fg_color=KIDS_COLORS["error"],
            hover_color="#cc3333",
            corner_radius=15
        )
        close_btn.pack(pady=10)
    
    def _send_voice_message(self, text):
        """发送语音识别后的消息"""
        if not text:
            return
            
        # 显示用户消息
        self.add_user_message(text)
        
        # 标记正在处理
        self.is_processing = True
        self.set_status("我在思考...")
        self.count += 1
        
        # 在后台处理AI响应
        threading.Thread(target=self.get_ai_response, args=(text,), daemon=True).start()
    
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
        self.set_status("我在思考...")
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
            # 错误回退：尝试使用备用方法
            try:
                # 转换为语音文件
                mp3_filename = f"response_{self.count}.mp3"
                from voice_assistant.text_to_speech import synthesize_speech
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
        self.messages = [{"role": "system", "content": "你是一个友好的助手，专为儿童设计。请使用简单友好的语言。"}]
        self.count = 0
        
        # 显示欢迎消息
        self.add_bot_message("你好啊，小朋友！点击下面的麦克风按钮，跟我说话吧！")
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
        app = KidsVoiceAssistant()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
