"""
ChatGPT风格的语音对话助手
----------------------------
简洁的界面设计，专注于核心功能：
1. 语音输入
2. AI处理
3. 语音输出
"""
import os
import sys
import time
import threading
import pathlib
import pygame
import customtkinter as ctk
from dotenv import load_dotenv

# 导入语音助手模块
from voice_assistant.speech_handler import record_and_transcribe
from voice_assistant.text_to_speech import synthesize_speech
from voice_assistant.ai_service import generate_response

# 设置主题
ctk.set_appearance_mode("System")  # 使用系统主题
ctk.set_default_color_theme("blue")  # 蓝色主题

# ChatGPT风格颜色
CHATGPT_COLORS = {
    "bg_light": "#ffffff",       # 浅色背景
    "bg_dark": "#343541",        # 深色背景
    "sidebar": "#202123",        # 侧边栏
    "user_msg": "#343541",       # 用户消息
    "bot_msg": "#444654",        # AI消息
    "text_light": "#ececf1",     # 浅色文本
    "text_dark": "#2d2d2d",      # 深色文本
    "accent": "#10a37f",         # 强调色（绿色）
    "border": "#e5e5e5"          # 边框颜色
}

# 加载环境变量
load_dotenv()

# 创建数据目录
data_dir = pathlib.Path("data")
data_dir.mkdir(exist_ok=True)

# 初始化pygame混音器（用于音频播放）
pygame.mixer.init()


class ChatMessage(ctk.CTkFrame):
    """ChatGPT风格的聊天消息组件"""
    def __init__(self, master, message, is_user=False, **kwargs):
        # 设置背景色
        bg_color = CHATGPT_COLORS["user_msg"] if is_user else CHATGPT_COLORS["bot_msg"]
        super().__init__(master, fg_color=bg_color, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # 内容容器
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        
        # 头像
        avatar_size = 30
        avatar_frame = ctk.CTkFrame(
            content_frame, 
            width=avatar_size, 
            height=avatar_size,
            fg_color=CHATGPT_COLORS["accent"] if is_user else "#9e57f5",
            corner_radius=avatar_size//2
        )
        avatar_frame.grid(row=0, column=0, padx=(0, 15), sticky="n")
        avatar_frame.grid_propagate(False)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame, 
            text="👤" if is_user else "🤖",
            text_color=CHATGPT_COLORS["text_light"],
            font=("Arial", 14)
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 消息文本
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            wraplength=700,
            justify="left",
            text_color=CHATGPT_COLORS["text_light"],
            anchor="w",
            font=("Arial", 13)
        )
        message_label.grid(row=0, column=1, sticky="w")


class ChatGPTStyleApp(ctk.CTk):
    """ChatGPT风格的语音对话助手"""
    def __init__(self):
        super().__init__()
        
        # 应用程序设置
        self.title("语音对话助手 - ChatGPT风格")
        self.geometry("900x700")
        self.minsize(700, 500)
        
        # 状态变量
        self.is_recording = False
        self.is_processing = False
        self.count = 0
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题。"}]
        
        # 创建界面
        self.create_widgets()
        
        # 显示欢迎消息
        self.add_bot_message("欢迎使用语音对话助手！点击下方麦克风按钮开始语音输入，或直接在输入框中输入文字。")
    
    def create_widgets(self):
        """创建GUI组件"""
        # 配置整体布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 主界面容器 - 深色背景
        self.main_frame = ctk.CTkFrame(self, fg_color=CHATGPT_COLORS["bg_dark"])
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 聊天区域 - 滚动容器
        self.chat_container = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color=CHATGPT_COLORS["bg_dark"],
            scrollbar_button_color=CHATGPT_COLORS["accent"],
            scrollbar_button_hover_color=CHATGPT_COLORS["accent"]
        )
        self.chat_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 70))
        
        # 设置底部输入区域容器
        self.input_frame = ctk.CTkFrame(
            self.main_frame, 
            height=70, 
            fg_color=CHATGPT_COLORS["bg_dark"],
            border_width=1,
            border_color=CHATGPT_COLORS["border"]
        )
        self.input_frame.grid(row=1, column=0, sticky="sew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)
        
        # 输入框容器
        input_area = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_area.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        input_area.grid_columnconfigure(1, weight=1)
        
        # 麦克风按钮
        self.mic_button = ctk.CTkButton(
            input_area,
            text="🎤",
            width=40,
            height=40,
            corner_radius=20,
            fg_color=CHATGPT_COLORS["accent"],
            hover_color="#0f8e6c",
            font=("Arial", 16),
            command=self.toggle_recording
        )
        self.mic_button.grid(row=0, column=0, padx=(0, 10))
        
        # 文本输入框
        self.message_input = ctk.CTkTextbox(
            input_area,
            height=40,
            fg_color="#40414f",
            border_color=CHATGPT_COLORS["border"],
            border_width=1,
            corner_radius=20,
            text_color=CHATGPT_COLORS["text_light"]
        )
        self.message_input.grid(row=0, column=1, sticky="ew")
        self.message_input.bind("<Return>", self.on_enter_pressed)
        
        # 发送按钮
        self.send_button = ctk.CTkButton(
            input_area,
            text="➤",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#40414f",
            hover_color=CHATGPT_COLORS["accent"],
            font=("Arial", 16),
            command=self.send_message
        )
        self.send_button.grid(row=0, column=2, padx=(10, 0))
        
        # 状态栏
        self.status_frame = ctk.CTkFrame(
            self.main_frame, 
            height=25, 
            fg_color=CHATGPT_COLORS["sidebar"]
        )
        self.status_frame.grid(row=2, column=0, sticky="sew")
        self.status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="就绪", 
            text_color=CHATGPT_COLORS["text_light"],
            padx=10
        )
        self.status_label.pack(side="left")
        
        # 创建"新对话"按钮
        new_chat_button = ctk.CTkButton(
            self.status_frame,
            text="新对话",
            width=80,
            height=20,
            corner_radius=5,
            fg_color=CHATGPT_COLORS["accent"],
            hover_color="#0f8e6c",
            command=self.clear_chat
        )
        new_chat_button.pack(side="right", padx=10, pady=2)
    
    def add_user_message(self, message):
        """添加用户消息"""
        msg = ChatMessage(self.chat_container, message, is_user=True)
        msg.pack(fill="x", pady=0)
        
        # 滚动到底部
        self.chat_container._parent_canvas.yview_moveto(1.0)
    
    def add_bot_message(self, message):
        """添加机器人消息"""
        msg = ChatMessage(self.chat_container, message, is_user=False)
        msg.pack(fill="x", pady=0)
        
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
            self.mic_button.configure(text="🎤", fg_color=CHATGPT_COLORS["accent"])
            return
            
        if self.is_processing:
            return
            
        # 开始录音
        self.is_recording = True
        self.mic_button.configure(text="⏹", fg_color="#e53935")
        self.set_status("正在录音...(说话完毕后将自动发送)")
        
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
        new_color = "#ff9800" if current_color == "#e53935" else "#e53935"
        self.mic_button.configure(fg_color=new_color)
        
        # 每500毫秒更新一次
        self.after(500, self._update_recording_animation)
    
    def record_audio(self):
        """录制并识别语音，完成后自动发送"""
        try:
            # 显示录音提示
            self.after(0, lambda: self.set_status("正在准备麦克风..."))
            
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
            add_debug_line("===== 开始语音识别调试 =====")
            add_debug_line(f"系统时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                # 录制并识别语音（较长的超时时间）
                add_debug_line("开始调用语音识别模块...")
                user_text = record_and_transcribe(duration=15, language="zh-CN")
                add_debug_line(f"语音识别返回: '{user_text}'")
            finally:
                # 恢复原始stdout
                sys.stdout = original_stdout
                
            self.is_recording = False
            
            # 重置录音按钮外观
            self.after(0, lambda: self.mic_button.configure(
                text="🎤", 
                fg_color=CHATGPT_COLORS["accent"]
            ))
            
            if user_text and user_text.strip():
                # 显示识别到的文本
                self.after(0, lambda: self.set_status(f"语音识别成功: '{user_text}'"))
                add_debug_line(f"最终识别结果: '{user_text}'")
                
                # 自动发送消息
                self.after(100, lambda: self._send_voice_message(user_text))
            else:
                add_debug_line("❌ 语音识别失败 - 返回空结果")
                self.after(0, lambda: self.set_status("无法识别语音，请重试或手动输入"))
                
                # 尝试手动输入
                self.prompt_manual_input(debug_window)
        except Exception as e:
            self.is_recording = False
            self.after(0, lambda: self.mic_button.configure(text="🎤", fg_color=CHATGPT_COLORS["accent"]))
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
        debug_win.grab_set()
        
        # 调试文本区域
        debug_win.debug_text = ctk.CTkTextbox(debug_win, height=350, width=580)
        debug_win.debug_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            debug_win, 
            text="关闭", 
            command=debug_win.destroy,
            fg_color=CHATGPT_COLORS["accent"],
            hover_color="#0f8e6c"
        )
        close_btn.pack(pady=10)
        
        return debug_win
    
    def prompt_manual_input(self, debug_window=None):
        """提示用户手动输入信息"""
        input_dialog = ctk.CTkInputDialog(
            title="手动输入", 
            text="语音识别失败，请手动输入您想说的内容:"
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
        error_window.grab_set()
        
        # 错误消息文本区域
        error_text = ctk.CTkTextbox(error_window, height=350, width=580)
        error_text.pack(padx=10, pady=10, fill="both", expand=True)
        error_text.insert("1.0", message)
        error_text.configure(state="disabled")
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            error_window, 
            text="关闭", 
            command=error_window.destroy,
            fg_color="#e53935",
            hover_color="#c62828"
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
        self.set_status("AI正在思考...")
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
        user_text = self.message_input.get("0.0", "end").strip()
        if not user_text:
            return
            
        # 清空输入框
        self.message_input.delete("0.0", "end")
        
        # 显示用户消息
        self.add_user_message(user_text)
        
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
            self.after(0, lambda: self.add_bot_message(ai_response))
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
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.after(0, lambda: self.set_status("就绪"))
        except Exception as e:
            self.after(0, lambda: self.set_status(f"播放音频出错: {e}"))
    
    def clear_chat(self):
        """清空对话记录"""
        # 清空聊天容器中的所有控件
        for widget in self.chat_container.winfo_children():
            widget.destroy()
            
        # 重置消息历史
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题。"}]
        self.count = 0
        
        # 显示欢迎消息
        self.add_bot_message("欢迎使用语音对话助手！点击下方麦克风按钮开始语音输入，或直接在输入框中输入文字。")
        self.set_status("对话已清空")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        # 停止任何播放中的音频
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        # 关闭窗口
        self.destroy()


# 主程序
if __name__ == "__main__":
    try:
        app = ChatGPTStyleApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
