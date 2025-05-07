"""
GUI Voice Conversation Assistant
-------------------------------------------
A graphical user interface for the voice conversation assistant focused on core functionality:
1. Voice/Text input
2. AI processing
3. Voice/Text output

This script provides a user-friendly GUI with both text-based and voice-based conversation modes.
"""
import os
import sys
import io
import time
import pathlib
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
from PIL import Image, ImageTk  # For handling images in the GUI
import sv_ttk  # Modern theme for tkinter
from dotenv import load_dotenv

# Import voice assistant modules
from voice_assistant.real_speech_to_text import record_and_transcribe
from voice_assistant.text_to_speech import synthesize_speech
from voice_assistant.ai_service import generate_response

# Load environment variables
load_dotenv()

# Set console encoding to UTF-8
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
except Exception as e:
    print(f"Warning: Could not set encoding: {e}")
    # Continue anyway

# Define exit phrases
EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}

class StatusBar(ttk.Frame):
    """Status bar for displaying current state and progress"""
    def __init__(self, parent):
        super().__init__(parent)
        
        # Status label with better font
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Add a separator between status and progress
        ttk.Separator(self, orient="vertical").pack(side=tk.LEFT, fill="y", padx=5, pady=2)
        
        # More stylish progress bar
        self.progress = ttk.Progressbar(
            self, 
            mode="indeterminate", 
            length=200
        )
        self.progress.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True, pady=5)
        
    def set_status(self, text):
        """Set the status text"""
        self.status_var.set(text)
        self.update_idletasks()
        
    def start_progress(self):
        """Start the progress animation"""
        self.progress.start()
        
    def stop_progress(self):
        """Stop the progress animation"""
        self.progress.stop()


class VoiceAssistantApp(tk.Tk):
    """Main application window for the Voice Assistant GUI"""
    def __init__(self):
        super().__init__()
        self.title("语音对话助手 (Voice Conversation Assistant)")
        self.geometry("900x650")
        self.minsize(700, 550)
        
        # Apply modern theme
        sv_ttk.set_theme("dark")  # Options: "light" or "dark"
        
        # Configure fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Microsoft YaHei UI", size=10)
        self.heading_font = font.Font(family="Microsoft YaHei UI", size=12, weight="bold")
        self.chat_font = font.Font(family="Microsoft YaHei UI", size=11)
        self.button_font = font.Font(family="Microsoft YaHei UI", size=10)
        
        # Set application icon
        try:
            # Create a data/resources directory if it doesn't exist
            resources_dir = pathlib.Path("data/resources")
            resources_dir.mkdir(exist_ok=True, parents=True)
            
            # If an icon file exists, use it; otherwise, create a simple one
            icon_path = resources_dir / "app_icon.ico"
            if not os.path.exists(icon_path):
                self.create_default_icon()
            self.iconbitmap(str(icon_path))
        except:
            pass  # Continue without icon if not available
            
        # Initialize conversation history
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题"}]
        self.conversation_count = 0
        self.is_processing = False
        self.is_recording = False
        
        # Create and configure the main frame with a gradient background
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Set up the UI components
        self._setup_ui()
        
        # Ensure data directory exists
        data_dir = pathlib.Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Print welcome message to chat
        self._append_to_chat("系统", "欢迎使用语音对话助手！\n可以通过文本输入或点击录音按钮开始对话。\n说'退出'或'exit'结束对话。")
        
    def create_default_icon(self):
        """Create a simple icon if none exists"""
        try:
            # Create a simple colored icon image
            icon_size = 64
            icon_img = Image.new('RGBA', (icon_size, icon_size), color=(75, 0, 130, 255))
            
            # Add a simple microphone-like shape
            from PIL import ImageDraw
            draw = ImageDraw.Draw(icon_img)
            # Draw circle
            draw.ellipse((15, 10, 49, 44), fill=(255, 255, 255, 255))
            # Draw stem
            draw.rectangle((27, 40, 37, 54), fill=(255, 255, 255, 255))
            # Draw base
            draw.ellipse((17, 50, 47, 60), fill=(255, 255, 255, 255))
            
            # Save as .ico format
            icon_path = pathlib.Path("data/resources/app_icon.ico")
            icon_img.save(str(icon_path), format='ICO')
        except Exception as e:
            print(f"创建图标时出错: {e}")
            # Continue without icon
    
    def _setup_ui(self):
        """Set up the user interface components"""
        # Create title/header area with gradient effect
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title label with larger, more elegant font
        self.title_label = ttk.Label(
            self.header_frame, 
            text="AI 语音对话助手", 
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Create conversation display area with rounded corners effect
        self.chat_frame = ttk.LabelFrame(
            self.main_frame, 
            text="对话历史",
            padding=10
        )
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat display with better fonts and colors
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=self.chat_font,
            padx=10,
            pady=10,
            borderwidth=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)  # Read-only
        
        # Create user input area with modern design
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        # Text input with placeholder
        self.text_input = ttk.Entry(
            self.input_frame,
            font=self.chat_font
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        self.text_input.bind("<Return>", self._on_text_submit)
        self.text_input.bind("<FocusIn>", self._on_entry_click)
        self.text_input.bind("<FocusOut>", self._on_focus_out)
        self.text_input.insert(0, "在这里输入消息...")
        
        # Control buttons frame
        self.button_frame = ttk.Frame(self.input_frame)
        self.button_frame.pack(side=tk.RIGHT)
        
        # Send button with icon
        self.send_button = ttk.Button(
            self.button_frame, 
            text="发送",
            width=8,
            command=self._on_text_submit,
            style="Accent.TButton"
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Voice input button with icon
        self.voice_button = ttk.Button(
            self.button_frame, 
            text="🎤 录音",
            width=8,
            command=self._toggle_recording
        )
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Clear chat button
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="清空对话",
            width=8,
            command=self._clear_chat
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar at the bottom with better styling
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
    def _on_entry_click(self, event):
        """Handle entry field click (clear placeholder)"""
        if self.text_input.get() == "在这里输入消息...":
            self.text_input.delete(0, tk.END)
            
    def _on_focus_out(self, event):
        """Handle focus out (restore placeholder if empty)"""
        if not self.text_input.get():
            self.text_input.insert(0, "在这里输入消息...")
    
    def _append_to_chat(self, speaker, message):
        """Add a message to the chat display with enhanced styling"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Insert a small separator between messages if not the first message
        if self.chat_display.index(tk.END) != '1.0':
            self.chat_display.insert(tk.END, "\n", "separator")
        
        # Format based on speaker with modern speech-bubble style formatting
        if speaker == "用户":
            self.chat_display.insert(tk.END, f"\n👤 用户: ", "user_tag")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif speaker == "助手":
            self.chat_display.insert(tk.END, f"\n🤖 助手: ", "bot_tag")
            self.chat_display.insert(tk.END, f"{message}\n", "bot_msg")
        else:  # System message
            self.chat_display.insert(tk.END, f"\n🔔 系统: ", "sys_tag")
            self.chat_display.insert(tk.END, f"{message}\n", "sys_msg")
        
        # Configure tags with more attractive colors and better fonts
        self.chat_display.tag_config(
            "user_tag", 
            foreground="#007bff",  # Blue
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.chat_display.tag_config(
            "user_msg", 
            foreground="#0056b3",  # Darker blue
            font=("Microsoft YaHei UI", 11)
        )
        self.chat_display.tag_config(
            "bot_tag", 
            foreground="#28a745",  # Green
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.chat_display.tag_config(
            "bot_msg", 
            foreground="#1d703f",  # Darker green
            font=("Microsoft YaHei UI", 11)
        )
        self.chat_display.tag_config(
            "sys_tag", 
            foreground="#6c757d",  # Gray
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.chat_display.tag_config(
            "sys_msg", 
            foreground="#495057",  # Darker gray
            font=("Microsoft YaHei UI", 11)
        )
        self.chat_display.tag_config(
            "separator", 
            font=("Microsoft YaHei UI", 6)
        )
        
        # Scroll to the end
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _on_text_submit(self, event=None):
        """Handle text submission"""
        if self.is_processing:
            messagebox.showinfo("处理中", "请等待当前响应完成")
            return
            
        user_text = self.text_input.get().strip()
        
        # Check for placeholder text
        if user_text == "在这里输入消息...":
            return
            
        if not user_text:
            return
            
        # Clear the input field
        self.text_input.delete(0, tk.END)
        
        # Process the input
        self._process_user_input(user_text)
    
    def _toggle_recording(self):
        """Toggle voice recording on/off"""
        if self.is_processing:
            messagebox.showinfo("处理中", "请等待当前响应完成")
            return
            
        if self.is_recording:
            # Cancel recording
            self.is_recording = False
            self.voice_button.config(text="🎤 录音")
            self.status_bar.set_status("录音已取消")
            return
            
        # Start recording in a separate thread
        self.is_recording = True
        self.voice_button.config(text="⏹️ 停止")
        self.status_bar.set_status("正在录音...")
        
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
    
    def _record_audio(self):
        """Record audio and transcribe it"""
        try:
            # Record audio and transcribe
            self.status_bar.start_progress()
            user_text = record_and_transcribe(duration=5, language="zh-CN")
            
            # Reset recording state
            self.is_recording = False
            self.voice_button.config(text="🎤 录音")
            self.status_bar.stop_progress()
            
            if not user_text:
                self.status_bar.set_status("未能识别语音，请重试")
                self._append_to_chat("系统", "未能识别语音，请重试或使用文本输入")
                return
                
            # Process the transcribed text
            self._process_user_input(user_text)
            
        except Exception as e:
            self.is_recording = False
            self.voice_button.config(text="🎤 录音")
            self.status_bar.stop_progress()
            self.status_bar.set_status(f"录音错误: {e}")
            self._append_to_chat("系统", f"录音出错: {e}")
    
    def _process_user_input(self, user_text):
        """Process user input text and generate response"""
        # Check if the user wants to exit
        if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
            self._append_to_chat("系统", "检测到退出指令，将在3秒后关闭程序")
            self.after(3000, self.destroy)
            return
            
        # Display user input
        self._append_to_chat("用户", user_text)
        
        # Add to conversation history
        self.messages.append({"role": "user", "content": user_text})
        
        # Prevent multiple processing
        self.is_processing = True
        self.conversation_count += 1
        
        # Update status
        self.status_bar.set_status("AI正在思考...")
        self.status_bar.start_progress()
        
        # Generate response in a separate thread
        response_thread = threading.Thread(target=self._generate_ai_response, args=(user_text,))
        response_thread.daemon = True
        response_thread.start()
    
    def _generate_ai_response(self, user_text):
        """Generate AI response in a separate thread"""
        try:
            # Generate the response
            ai_response = generate_response(self.messages)
            
            # Update the UI with the response
            self.after(0, lambda: self._handle_ai_response(ai_response))
            
        except Exception as e:
            error_msg = f"生成回复时出错: {e}"
            self.after(0, lambda: self._append_to_chat("系统", error_msg))
            self.after(0, lambda: self.status_bar.set_status("出错"))
            self.after(0, lambda: self.status_bar.stop_progress())
            self.is_processing = False
    
    def _handle_ai_response(self, ai_response):
        """Handle the generated AI response"""
        # Add to conversation history
        self.messages.append({"role": "assistant", "content": ai_response})
        
        # Display the response
        self._append_to_chat("助手", ai_response)
        
        # Update status
        self.status_bar.set_status("正在生成语音...")
        
        # Generate speech in a separate thread
        speech_thread = threading.Thread(target=self._generate_speech, args=(ai_response,))
        speech_thread.daemon = True
        speech_thread.start()
    
    def _generate_speech(self, text):
        """Generate and play speech for the AI response"""
        try:
            # Generate speech
            mp3_filename = f"response_{self.conversation_count}.mp3"
            success = synthesize_speech(text, mp3_filename)
            
            if success:
                # Update status
                self.after(0, lambda: self.status_bar.set_status("正在播放语音..."))
                
                # Play the audio
                audio_path = pathlib.Path("data") / mp3_filename
                if os.path.exists(audio_path):
                    try:
                        os.startfile(audio_path)
                        
                        # Wait for approximate playback duration
                        words_per_second = 2.5  # Estimated speaking rate
                        wait_time = min(len(text.split()) / words_per_second, 30)  # Cap at 30 seconds
                        time.sleep(wait_time)
                        
                    except (AttributeError, OSError) as e:
                        self.after(0, lambda: self._append_to_chat("系统", f"无法播放音频: {e}"))
            else:
                self.after(0, lambda: self._append_to_chat("系统", "语音生成失败"))
                
        except Exception as e:
            self.after(0, lambda: self._append_to_chat("系统", f"语音生成错误: {e}"))
            
        # Reset processing state
        self.after(0, lambda: self.status_bar.set_status("就绪"))
        self.after(0, lambda: self.status_bar.stop_progress())
        self.is_processing = False
    
    def _clear_chat(self):
        """Clear the chat display and reset conversation"""
        if messagebox.askyesno("确认", "是否要清空当前对话历史？"):
            # Reset conversation history but keep system prompt
            self.messages = [self.messages[0]]
            self.conversation_count = 0
            
            # Clear the chat display
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Add welcome message
            self._append_to_chat("系统", "对话已清空。可以开始新的对话了！")


if __name__ == "__main__":
    try:
        # Make sure the sv_ttk theme package is installed
        try:
            import sv_ttk
        except ImportError:
            print("正在安装sv_ttk主题包...")
            import subprocess
            subprocess.call([sys.executable, "-m", "pip", "install", "sv-ttk"])
            import sv_ttk
        
        # Start the application
        app = VoiceAssistantApp()
        app.mainloop()
    except Exception as e:
        # Show error in GUI if possible, otherwise fall back to console
        try:
            messagebox.showerror("启动错误", f"程序启动时发生错误: {e}")
        except:
            print(f"程序启动时发生错误: {e}")
            import traceback
            traceback.print_exc()
