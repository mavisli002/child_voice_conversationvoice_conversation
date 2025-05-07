"""
ChatGPT Style Voice Assistant
-------------------------------------------
A minimalist GUI for the voice conversation assistant inspired by ChatGPT design:
1. Voice/Text input
2. AI processing 
3. Voice/Text output

Features a clean, modern interface with message bubbles and simplified controls.
"""
import os
import sys
import io
import time
import pathlib
import threading
import datetime
from PIL import Image, ImageTk
import customtkinter as ctk
from dotenv import load_dotenv

# Import voice assistant modules
import platform
if platform.system() == 'Windows':
    # 使用Windows优化的语音识别模块
    from voice_assistant.windows_speech import windows_record_and_transcribe as record_and_transcribe
else:
    # 使用标准语音识别模块
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

# Define exit phrases
EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Options: "Light", "Dark", "System"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class ScrollableMessageFrame(ctk.CTkScrollableFrame):
    """A scrollable frame that displays conversation messages in a ChatGPT style"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        # Store message widgets references
        self.message_widgets = []
        
    def add_message(self, is_user, message, thinking=False):
        """Add a message to the chat in a bubble style"""
        # Create frame for this message
        if is_user:
            # User message (right-aligned)
            message_frame = ctk.CTkFrame(self, fg_color="transparent")
            message_frame.grid(row=len(self.message_widgets), column=0, pady=(10, 5), padx=10, sticky="e")
            
            # Message bubble
            bubble = ctk.CTkTextbox(
                message_frame, 
                width=400, 
                height=50,  # Default height, will be adjusted below
                fg_color="#1E6FD9",  # Blue for user messages
                border_width=0,
                corner_radius=15,
                wrap="word",
                activate_scrollbars=False
            )
            bubble.grid(row=0, column=0, padx=10, pady=5)
            
            # Insert message text
            bubble.insert("0.0", message)
            bubble.configure(state="disabled")  # Make read-only
            
            # Adjust height based on content
            line_count = message.count('\n') + 1
            char_count = len(message)
            height = max(35, min(300, 20 * line_count + char_count // 50 * 5))
            bubble.configure(height=height)
            
        else:
            # Assistant message (left-aligned)
            message_frame = ctk.CTkFrame(self, fg_color="transparent")
            message_frame.grid(row=len(self.message_widgets), column=0, pady=(10, 5), padx=10, sticky="w")
            
            # Icon (optional, can add AI avatar here)
            icon_size = 32
            try:
                # Try to load an avatar image
                avatar_path = pathlib.Path("data/resources/ai_avatar.png")
                if avatar_path.exists():
                    img = Image.open(avatar_path).resize((icon_size, icon_size))
                    photo = ImageTk.PhotoImage(img)
                    icon_label = ctk.CTkLabel(message_frame, image=photo, text="")
                    icon_label.image = photo  # Keep a reference
                    icon_label.grid(row=0, column=0, padx=(0, 5))
                else:
                    # Create a simple colored circle as avatar
                    icon_label = ctk.CTkLabel(
                        message_frame, 
                        text="AI",
                        width=icon_size,
                        height=icon_size,
                        corner_radius=icon_size//2,
                        fg_color="#10A37F",  # Green circle
                        text_color="white",
                        font=("Arial", 10, "bold")
                    )
                    icon_label.grid(row=0, column=0, padx=(0, 5))
            except Exception:
                # If image loading fails, use text avatar
                icon_label = ctk.CTkLabel(
                    message_frame, 
                    text="AI",
                    width=icon_size,
                    height=icon_size,
                    corner_radius=icon_size//2,
                    fg_color="#10A37F",  # Green circle
                    text_color="white",
                    font=("Arial", 10, "bold")
                )
                icon_label.grid(row=0, column=0, padx=(0, 5))
            
            # Message bubble
            bubble_color = "#565869" if not thinking else "#3F3F3F"  # Dark gray for AI messages
            bubble = ctk.CTkTextbox(
                message_frame, 
                width=400, 
                height=50,  # Default height, will be adjusted below
                fg_color=bubble_color,
                border_width=0,
                corner_radius=15,
                wrap="word",
                activate_scrollbars=False
            )
            bubble.grid(row=0, column=1, padx=0, pady=5)
            
            # Insert message text
            bubble.insert("0.0", message)
            bubble.configure(state="disabled")  # Make read-only
            
            # Adjust height based on content
            line_count = message.count('\n') + 1
            char_count = len(message)
            height = max(35, min(300, 20 * line_count + char_count // 50 * 5))
            bubble.configure(height=height)
        
        # Store reference and scroll to bottom
        self.message_widgets.append((message_frame, is_user))
        self.after(100, self._scroll_to_bottom)
        
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the messages"""
        self._parent_canvas.yview_moveto(1.0)

    def clear_messages(self):
        """Clear all messages"""
        for frame, _ in self.message_widgets:
            frame.destroy()
        self.message_widgets = []


class VoiceAssistantApp(ctk.CTk):
    """Main application window for the Voice Assistant GUI with ChatGPT style"""
    def __init__(self):
        super().__init__()
        self.title("语音对话助手")
        self.geometry("800x700")
        self.minsize(650, 500)
        
        # Use system font for better Chinese character display
        self.font_family = "Microsoft YaHei UI" if os.name == "nt" else "PingFang SC"
        self.default_font = (self.font_family, 12)
        self.small_font = (self.font_family, 11)
        self.title_font = (self.font_family, 16, "bold")
        
        # Initialize conversation history
        self.messages = [{"role": "system", "content": "你是一个有帮助的助手，请简洁明了地回答问题"}]
        self.conversation_count = 0
        self.is_processing = False
        self.is_recording = False
        self.thinking_message_index = None
        
        # Configure the grid layout
        self.grid_columnconfigure(0, weight=1)  # Column 0 expands horizontally
        self.grid_rowconfigure(1, weight=1)     # Row 1 expands vertically (main content)
        
        # Set up the UI components
        self._setup_ui()
        
        # Ensure data directory exists
        data_dir = pathlib.Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Add welcome message
        self.message_frame.add_message(False, "欢迎使用语音对话助手！\n可以通过文本输入或点击语音按钮开始对话。\n说'退出'或'exit'结束对话。")
        
    def _setup_ui(self):
        """Set up the user interface components in ChatGPT style"""
        # Top bar with title
        self.top_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.top_bar.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.top_bar, 
            text="AI 语音助手", 
            font=self.title_font
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.clear_button = ctk.CTkButton(
            self.top_bar,
            text="新对话",
            font=self.small_font,
            width=80,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            border_width=1,
            command=self._clear_chat
        )
        self.clear_button.grid(row=0, column=1, padx=10)
        
        # Conversation display area (scrollable)
        self.message_frame = ScrollableMessageFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
            width=780,
            height=550,
        )
        self.message_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 10))
        
        # Bottom input area
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.bottom_frame.grid_columnconfigure(1, weight=1)  # Text input expands
        
        # Text input with rounded corners
        self.text_input = ctk.CTkTextbox(
            self.bottom_frame,
            height=45,
            corner_radius=23,  # Rounded corners
            border_width=1,
            font=self.default_font,
            wrap="word"
        )
        self.text_input.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        self.text_input.bind("<Return>", self._on_text_submit)
        self.text_input.bind("<Shift-Return>", self._on_shift_return)
        
        # Add placeholder text
        self.text_input.insert("0.0", "在这里输入消息或点击右侧语音按钮...")
        self.text_input.bind("<FocusIn>", self._on_entry_click)
        self.text_input.bind("<FocusOut>", self._on_focus_out)
        
        # Voice input button (round microphone)
        self.voice_button = ctk.CTkButton(
            self.bottom_frame,
            text="🎤",  # Microphone icon
            font=(self.font_family, 16),
            width=45,
            height=45,
            corner_radius=23,  # Make it round
            command=self._toggle_recording
        )
        self.voice_button.grid(row=0, column=2, padx=(0, 10))
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.bottom_frame,
            text="发送",
            font=self.small_font,
            width=60,
            height=45,
            corner_radius=23,
            command=self._on_text_submit
        )
        self.send_button.grid(row=0, column=3, padx=(0, 0))
        
        # Status display (subtle at the bottom)
        self.status_var = ctk.StringVar(value="就绪")
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=(self.font_family, 10),
            text_color="gray"
        )
        self.status_label.grid(row=3, column=0, sticky="e", padx=20, pady=(0, 5))
        
    def _on_entry_click(self, event):
        """Handle text area focus in - clear placeholder"""
        if self.text_input.get("0.0", "end-1c") == "在这里输入消息或点击右侧语音按钮...":
            self.text_input.delete("0.0", "end")
            
    def _on_focus_out(self, event):
        """Handle text area focus out - restore placeholder if empty"""
        if not self.text_input.get("0.0", "end-1c").strip():
            self.text_input.delete("0.0", "end")
            self.text_input.insert("0.0", "在这里输入消息或点击右侧语音按钮...")
            
    def _on_shift_return(self, event):
        """Allow multi-line input with Shift+Enter"""
        return "break"  # Allow default behavior of inserting a newline
            
    def _on_text_submit(self, event=None):
        """Handle text submission (Enter key or button click)"""
        if self.is_processing:
            return
        
        # Get text and check if it's not just the placeholder
        user_text = self.text_input.get("0.0", "end-1c").strip()
        if user_text == "在这里输入消息或点击右侧语音按钮..." or not user_text:
            return
            
        # Clear the input field
        self.text_input.delete("0.0", "end")
        
        # Process the input
        self._process_user_input(user_text)
        
        return "break"  # Prevent default Enter behavior (adding newline)
        
    def _toggle_recording(self):
        """Toggle voice recording on/off"""
        if self.is_processing:
            return
            
        if self.is_recording:
            # Cancel recording
            self.is_recording = False
            self.voice_button.configure(fg_color="#1F6AA5", text="🎤")
            self.set_status("录音已取消")
            return
            
        # Start recording in a separate thread
        self.is_recording = True
        self.voice_button.configure(fg_color="#E53935", text="⏹")
        self.set_status("正在录音...")
        
        # Start recording thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
        
    def _record_audio(self):
        """Record audio and transcribe it"""
        try:
            # Record audio and transcribe
            user_text = record_and_transcribe(duration=5, language="zh-CN")
            
            # Reset recording state
            self.is_recording = False
            self.voice_button.configure(fg_color="#1F6AA5", text="🎤")
            
            if not user_text:
                self.set_status("未能识别语音，请重试")
                self.message_frame.add_message(False, "未能识别语音，请重试或使用文本输入。")
                return
                
            # Process the transcribed text
            self._process_user_input(user_text)
            
        except Exception as e:
            self.is_recording = False
            self.voice_button.configure(fg_color="#1F6AA5", text="🎤")
            self.set_status(f"录音错误: {e}")
            self.message_frame.add_message(False, f"录音出错: {e}")
            
    def _process_user_input(self, user_text):
        """Process user input text and generate response"""
        # Check if the user wants to exit
        if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
            self.message_frame.add_message(True, user_text)
            self.message_frame.add_message(False, "再见！程序将在3秒后关闭。")
            self.after(3000, self.destroy)
            return
            
        # Display user input
        self.message_frame.add_message(True, user_text)
        
        # Add to conversation history
        self.messages.append({"role": "user", "content": user_text})
        
        # Prevent multiple processing
        self.is_processing = True
        self.conversation_count += 1
        
        # Show thinking state
        self.set_status("AI正在思考...")
        self.message_frame.add_message(False, "思考中...", thinking=True)
        self.thinking_message_index = len(self.message_frame.message_widgets) - 1
        
        # Generate response in a separate thread
        response_thread = threading.Thread(target=self._generate_ai_response)
        response_thread.daemon = True
        response_thread.start()
        
    def _generate_ai_response(self):
        """Generate AI response in a separate thread"""
        try:
            # Generate the response
            ai_response = generate_response(self.messages)
            
            # Update the UI with the response
            self.after(0, lambda: self._handle_ai_response(ai_response))
            
        except Exception as e:
            error_msg = f"生成回复时出错: {e}"
            self.after(0, lambda: self._show_error(error_msg))
            
    def _handle_ai_response(self, ai_response):
        """Handle the generated AI response"""
        # Add to conversation history
        self.messages.append({"role": "assistant", "content": ai_response})
        
        # Remove the thinking message
        if self.thinking_message_index is not None:
            thinking_frame, _ = self.message_frame.message_widgets[self.thinking_message_index]
            thinking_frame.destroy()
            self.message_frame.message_widgets.pop(self.thinking_message_index)
            self.thinking_message_index = None
        
        # Display the response
        self.message_frame.add_message(False, ai_response)
        
        # Update status
        self.set_status("正在生成语音...")
        
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
                self.after(0, lambda: self.set_status("正在播放语音..."))
                
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
                        self.after(0, lambda: self.set_status(f"无法播放音频: {e}"))
            else:
                self.after(0, lambda: self.set_status("语音生成失败"))
                
        except Exception as e:
            self.after(0, lambda: self.set_status(f"语音生成错误: {e}"))
            
        # Reset processing state
        self.after(0, lambda: self.set_status("就绪"))
        self.is_processing = False
        
    def _show_error(self, error_message):
        """Show error message in the chat"""
        # Remove the thinking message if it exists
        if self.thinking_message_index is not None:
            thinking_frame, _ = self.message_frame.message_widgets[self.thinking_message_index]
            thinking_frame.destroy()
            self.message_frame.message_widgets.pop(self.thinking_message_index)
            self.thinking_message_index = None
            
        # Add error message
        self.message_frame.add_message(False, f"错误: {error_message}")
        self.set_status("错误")
        self.is_processing = False
        
    def _clear_chat(self):
        """Clear the chat display and reset conversation"""
        # Reset conversation history but keep system prompt
        self.messages = [self.messages[0]]
        self.conversation_count = 0
        
        # Clear the chat display
        self.message_frame.clear_messages()
        
        # Add welcome message
        self.message_frame.add_message(False, "开始新的对话。")
        self.set_status("就绪")
        
    def set_status(self, status_text):
        """Set the status text"""
        self.status_var.set(status_text)
        self.update_idletasks()

# 为了兼容性，创建一个类别名
ChatGPTWindow = VoiceAssistantApp

if __name__ == "__main__":
    try:
        # Ensure required packages
        import customtkinter
        
        # Create resources directory if it doesn't exist
        resources_dir = pathlib.Path("data/resources")
        resources_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a simple AI avatar if it doesn't exist
        avatar_path = resources_dir / "ai_avatar.png"
        if not os.path.exists(avatar_path):
            try:
                # Create a simple colored icon image
                icon_size = 64
                icon_img = Image.new('RGBA', (icon_size, icon_size), color=(16, 163, 127, 255))
                
                # Add text "AI"
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(icon_img)
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                    
                # Center the text
                text = "AI"
                text_width = draw.textlength(text, font=font)
                text_height = 24  # Approximate height
                position = ((icon_size - text_width) // 2, (icon_size - text_height) // 2)
                
                # Draw text
                draw.text(position, text, fill=(255, 255, 255, 255), font=font)
                
                # Save
                icon_img.save(str(avatar_path), format='PNG')
            except Exception as e:
                print(f"Could not create AI avatar: {e}")
        
        # Start the application
        app = VoiceAssistantApp()
        app.mainloop()
    except Exception as e:
        # Show error in GUI if possible, otherwise fall back to console
        try:
            from tkinter import messagebox
            messagebox.showerror("启动错误", f"程序启动时发生错误: {e}")
        except:
            print(f"程序启动时发生错误: {e}")
            import traceback
            traceback.print_exc()
