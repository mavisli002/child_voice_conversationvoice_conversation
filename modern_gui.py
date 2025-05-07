"""
Modern Voice Conversation Assistant GUI
-------------------------------------------
A modern GUI for the voice conversation assistant with international design:
1. Voice/Text input
2. AI processing 
3. Voice/Text output

Features a clean, modern interface with improved user experience.
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
from voice_assistant.windows_speech import windows_record_and_transcribe
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

# Define exit phrases - include both Chinese and English for international users
EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit", "stop", "end"}

# Set appearance mode and default color theme
ctk.set_appearance_mode("system")  # Use system setting by default
ctk.set_default_color_theme("blue")  # Default theme

class ScrollableMessageFrame(ctk.CTkScrollableFrame):
    """A scrollable frame that displays conversation messages in a modern chat style"""
    
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
            
            # Message bubble with user color
            bubble = ctk.CTkTextbox(
                message_frame, 
                width=400, 
                height=None,  # Auto height
                fg_color="#2563EB",  # Modern blue for user messages
                text_color="#FFFFFF",
                border_width=0,
                corner_radius=15,
                wrap="word",
                activate_scrollbars=False
            )
            bubble.grid(row=0, column=0, padx=10, pady=5)
            
        else:
            # Assistant message (left-aligned)
            message_frame = ctk.CTkFrame(self, fg_color="transparent")
            message_frame.grid(row=len(self.message_widgets), column=0, pady=(10, 5), padx=10, sticky="w")
            
            # Icon (optional, can add AI avatar here)
            icon_size = 35
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
                        corner_radius=icon_size // 2,
                        fg_color="#10B981",  # Modern green for AI
                        text_color="#FFFFFF",
                        font=ctk.CTkFont(family="Arial", size=12, weight="bold")
                    )
                    icon_label.grid(row=0, column=0, padx=(0, 5))
            except:
                # Skip avatar if there's any issue
                pass
                
            # Message bubble with assistant color
            bubble = ctk.CTkTextbox(
                message_frame, 
                width=400, 
                height=None,  # Auto height
                fg_color="#1F2937" if ctk.get_appearance_mode() == "Dark" else "#F3F4F6",  # Adaptive color based on theme
                text_color="#FFFFFF" if ctk.get_appearance_mode() == "Dark" else "#000000",
                border_width=0,
                corner_radius=15,
                wrap="word",
                activate_scrollbars=False
            )
            bubble.grid(row=0, column=1, padx=5, pady=5)
            
        # Insert message text
        bubble.insert("0.0", message)
        bubble.configure(state="disabled")  # Make read-only
        
        # Adjust height based on content
        line_count = message.count('\n') + 1
        char_count = len(message)
        height = max(35, min(300, 20 * line_count + char_count // 60 * 5))
        bubble.configure(height=height)
        
        # Store reference to widgets for future management
        self.message_widgets.append((message_frame, is_user))
        
        # Scroll to see the new message
        self._scroll_to_bottom()
        
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the messages"""
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)
        
    def clear_messages(self):
        """Clear all messages"""
        for frame, _ in self.message_widgets:
            frame.destroy()
        self.message_widgets = []


class ModernVoiceAssistantApp(ctk.CTk):
    """Modern UI for Voice Assistant with international design"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Voice Conversation Assistant")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Create resources and data directories if they don't exist
        resources_dir = pathlib.Path("data/resources")
        resources_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize state variables
        self.is_recording = False
        self.is_processing = False
        self.conversation_count = 0
        self.thinking_message_index = None
        self.text_height = 1  # Initial text input height
        self.record_anim_index = 0
        self.record_anim_running = False
        
        # Initialize conversation history
        self.messages = [{"role": "system", "content": "You are a helpful assistant providing clear and concise answers."}]
        
        # Set up the UI
        self._setup_ui()
        
        # Add welcome message
        self.message_frame.add_message(False, "Hello! I'm your voice assistant. How can I help you today?")
        
    def _setup_ui(self):
        """Set up the user interface components in modern style"""
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)  # Chat area expands
        self.grid_columnconfigure(0, weight=1)  # Center column expands
        
        # Main content frame - gives us padding around all elements
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_rowconfigure(0, weight=1)  # Chat area expands
        main_frame.grid_columnconfigure(0, weight=1)  # Center column expands
        
        # Header with title and settings
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Voice Conversation Assistant",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Theme toggle button
        self.theme_icon = ctk.CTkImage(
            light_image=Image.new("RGB", (20, 20), color=(30, 30, 30)),
            dark_image=Image.new("RGB", (20, 20), color=(240, 240, 240)),
            size=(20, 20)
        )
        
        def toggle_theme():
            """Toggle between light and dark mode"""
            new_mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
            ctk.set_appearance_mode(new_mode)
            
        theme_button = ctk.CTkButton(
            header_frame,
            text="",
            image=self.theme_icon,
            width=40,
            height=40,
            corner_radius=10,
            command=toggle_theme
        )
        theme_button.grid(row=0, column=1, padx=5)
        
        # Clear chat button
        clear_button = ctk.CTkButton(
            header_frame,
            text="Clear Chat",
            width=100,
            height=40,
            corner_radius=10,
            command=self._clear_chat
        )
        clear_button.grid(row=0, column=2, padx=5)
        
        # Content frame contains chat display and input area
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Chat display - scrollable frame for messages
        self.message_frame = ScrollableMessageFrame(
            content_frame,
            width=750,
            corner_radius=10,
            fg_color=("#F9FAFB", "#111827")  # Light mode, Dark mode
        )
        self.message_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Input area - frame containing text input and buttons
        input_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=80)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Text input
        self.text_var = ctk.StringVar(value="")
        self.input_textbox = ctk.CTkTextbox(
            input_frame,
            height=45,
            corner_radius=15,
            border_width=1,
            border_color=("#E5E7EB", "#374151"),  # Light mode, Dark mode
            fg_color=("#FFFFFF", "#1F2937"),      # Light mode, Dark mode
            wrap="word",
            font=ctk.CTkFont(family="Arial", size=14)
        )
        self.input_textbox.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Placeholder text
        self.input_textbox.insert("0.0", "Type a message...")
        self.input_placeholder = True
        
        # Bind events for input text
        self.input_textbox.bind("<FocusIn>", self._on_entry_click)
        self.input_textbox.bind("<FocusOut>", self._on_focus_out)
        self.input_textbox.bind("<Return>", self._on_text_submit)
        self.input_textbox.bind("<Shift-Return>", self._on_shift_return)
        
        # Buttons frame (containing send and voice buttons)
        buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")
        
        # Voice button
        self.voice_icon = ctk.CTkImage(
            light_image=Image.new("RGB", (20, 20), color=(52, 211, 153)),
            dark_image=Image.new("RGB", (20, 20), color=(52, 211, 153)),
            size=(20, 20)
        )
        self.voice_button = ctk.CTkButton(
            buttons_frame,
            text="",
            image=self.voice_icon,
            width=45,
            height=45,
            corner_radius=22.5,
            fg_color="#10B981",  # Green
            hover_color="#059669",
            command=self._toggle_recording
        )
        self.voice_button.grid(row=0, column=0, padx=5)
        
        # Send button
        self.send_icon = ctk.CTkImage(
            light_image=Image.new("RGB", (20, 20), color=(255, 255, 255)),
            dark_image=Image.new("RGB", (20, 20), color=(255, 255, 255)),
            size=(20, 20)
        )
        self.send_button = ctk.CTkButton(
            buttons_frame,
            text="",
            image=self.send_icon,
            width=45,
            height=45,
            corner_radius=22.5,
            fg_color="#2563EB",  # Blue
            hover_color="#1D4ED8",
            command=self._on_text_submit
        )
        self.send_button.grid(row=0, column=1, padx=5)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=30)
        self.status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # Status text
        self.status_var = ctk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(family="Arial", size=12)
        )
        status_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Progress bar for AI thinking
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            width=200,
            mode="indeterminate",
            height=10,
            corner_radius=5
        )
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=10)
        self.progress_bar.set(0)  # Initialize as empty
        
    def _on_entry_click(self, event):
        """Handle text area focus in - clear placeholder"""
        if self.input_placeholder:
            self.input_textbox.delete("0.0", "end")
            self.input_placeholder = False
            
    def _on_focus_out(self, event):
        """Handle text area focus out - restore placeholder if empty"""
        if not self.input_textbox.get("0.0", "end-1c"):
            self.input_textbox.insert("0.0", "Type a message...")
            self.input_placeholder = True
            
    def _on_shift_return(self, event):
        """Allow multi-line input with Shift+Enter"""
        return "break"  # Let default behavior (newline) happen
        
    def _on_text_submit(self, event=None):
        """Handle text submission (Enter key or button click)"""
        if self.is_processing:
            return "break"  # Don't do anything if already processing
            
        # Get input text
        user_text = self.input_textbox.get("0.0", "end-1c").strip()
        
        # Check if placeholder or empty
        if not user_text or self.input_placeholder:
            return "break"
            
        # Clear input field
        self.input_textbox.delete("0.0", "end")
        self.input_placeholder = False
        
        # Process the user input
        self._process_user_input(user_text)
        
        return "break"  # Prevent default Enter behavior
        
    def _toggle_recording(self):
        """Toggle voice recording on/off"""
        if self.is_processing:
            return  # Don't allow recording during processing
            
        if self.is_recording:
            # Stop recording
            self.is_recording = False
            self.voice_button.configure(fg_color="#10B981")
            self.voice_button.configure(text="")
            
            # Stop animation if it's running
            if self.record_anim_running:
                self.record_anim_running = False
                
            # Set status back to ready
            self.set_status("Ready")
        else:
            # Start recording
            self.is_recording = True
            self.voice_button.configure(fg_color="#DC2626")  # Red for recording
            
            # Show recording status
            self.set_status("Listening...")
            
            # Start recording animation
            self.record_anim_running = True
            self._update_recording_animation()
            
            # Start recording in a separate thread
            record_thread = threading.Thread(target=self._record_audio)
            record_thread.daemon = True
            record_thread.start()
            
    def _update_recording_animation(self):
        """Update the recording button animation"""
        if not self.record_anim_running:
            return
            
        # Animation frames
        frames = ["◉", "◎", "◌", "◎"]
        
        # Update button text with animation frame
        self.voice_button.configure(text=frames[self.record_anim_index])
        self.record_anim_index = (self.record_anim_index + 1) % len(frames)
        
        # Schedule next frame update
        self.after(300, self._update_recording_animation)
        
    def _record_audio(self):
        """Record audio and transcribe it"""
        try:
            # Set status
            self.after(0, lambda: self.set_status("Listening..."))
            
            # Record and transcribe audio using Windows-optimized module
            user_text = windows_record_and_transcribe(duration=5, language="zh-CN")
            
            # Update status
            self.after(0, lambda: self.set_status("Processing..."))
            
            # Reset recording state
            self.after(0, lambda: self._set_recording_state(False))
            
            # Process the recognized text
            if user_text:
                self.after(0, lambda: self._process_user_input(user_text))
            else:
                self.after(0, lambda: self.set_status("Speech not recognized. Please try again."))
                
        except Exception as e:
            error_msg = f"Speech recognition error: {e}"
            self.after(0, lambda: self.set_status(error_msg))
            
            # Reset recording state
            self.after(0, lambda: self._set_recording_state(False))
            
    def _set_recording_state(self, is_recording):
        """Set recording state and update UI accordingly"""
        self.is_recording = is_recording
        
        if is_recording:
            self.voice_button.configure(fg_color="#DC2626")  # Red for recording
            self.record_anim_running = True
            self._update_recording_animation()
        else:
            self.voice_button.configure(fg_color="#10B981")  # Green when not recording
            self.voice_button.configure(text="")
            self.record_anim_running = False
            
    def _process_user_input(self, user_text):
        """Process user input text and generate response"""
        if self.is_processing or not user_text:
            return
            
        # Check if user wants to exit
        if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
            self.message_frame.add_message(True, user_text)
            self.message_frame.add_message(False, "Goodbye! The application will now close.")
            self.after(2000, self.destroy)
            return
            
        # Increment conversation counter
        self.conversation_count += 1
        
        # Show user message
        self.message_frame.add_message(True, user_text)
        
        # Add to conversation history
        self.messages.append({"role": "user", "content": user_text})
        
        # Show thinking indicator
        self._add_thinking_indicator()
        
        # Set processing state
        self.is_processing = True
        self.set_status("AI is thinking...")
        self.progress_bar.start()
        
        # Generate AI response in a separate thread
        response_thread = threading.Thread(target=self._generate_ai_response)
        response_thread.daemon = True
        response_thread.start()
        
    def _add_thinking_indicator(self):
        """Add a thinking indicator message that will be replaced by actual response"""
        # Add thinking message
        self.message_frame.add_message(False, "Thinking...", thinking=True)
        
        # Store the index of the thinking message (for replacing later)
        self.thinking_message_index = len(self.message_frame.message_widgets) - 1
        
    def _generate_ai_response(self):
        """Generate AI response in a separate thread"""
        try:
            # Generate response
            ai_response = generate_response(self.messages)
            
            # Handle response on main thread
            self.after(0, lambda: self._handle_ai_response(ai_response))
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.after(0, lambda: self.set_status(error_msg))
            
            # Remove thinking indicator and show error
            if self.thinking_message_index is not None:
                thinking_frame, _ = self.message_frame.message_widgets[self.thinking_message_index]
                thinking_frame.destroy()
                self.message_frame.message_widgets.pop(self.thinking_message_index)
                self.thinking_message_index = None
                
                # Add error message
                self.message_frame.add_message(False, f"Error: {error_msg}")
            
            # Reset processing state
            self.is_processing = False
            self.progress_bar.stop()
            self.after(0, lambda: self.set_status("Ready"))
            
    def _handle_ai_response(self, ai_response):
        """Handle the generated AI response"""
        # Remove thinking indicator
        if self.thinking_message_index is not None:
            thinking_frame, _ = self.message_frame.message_widgets[self.thinking_message_index]
            thinking_frame.destroy()
            self.message_frame.message_widgets.pop(self.thinking_message_index)
            self.thinking_message_index = None
            
        # Add AI response to the chat
        self.message_frame.add_message(False, ai_response)
        
        # Add to conversation history
        self.messages.append({"role": "assistant", "content": ai_response})
        
        # Update status
        self.set_status("Generating speech...")
        
        # Generate speech in a separate thread
        speech_thread = threading.Thread(target=self._generate_speech, args=(ai_response,))
        speech_thread.daemon = True
        speech_thread.start()
        
    def _generate_speech(self, text):
        """Generate and play speech for the AI response"""
        try:
            # Create data directory if it doesn't exist
            data_dir = pathlib.Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Generate speech
            mp3_filename = f"response_{self.conversation_count}.mp3"
            file_path = data_dir / mp3_filename
            success = synthesize_speech(text, str(file_path))
            
            if success:
                # Update status
                self.after(0, lambda: self.set_status("Playing audio..."))
                
                # Play the audio
                if os.path.exists(file_path):
                    try:
                        os.startfile(file_path)
                        
                        # Wait for approximate playback duration
                        words_per_second = 2.5  # Estimated speaking rate
                        wait_time = min(len(text.split()) / words_per_second, 30)  # Cap at 30 seconds
                        time.sleep(wait_time)
                        
                    except (AttributeError, OSError) as e:
                        self.after(0, lambda: self.set_status(f"Could not play audio: {e}"))
            else:
                self.after(0, lambda: self.set_status("Speech generation failed"))
                
        except Exception as e:
            self.after(0, lambda: self.set_status(f"Speech generation error: {e}"))
            
        # Reset processing state
        self.is_processing = False
        self.progress_bar.stop()
        self.after(0, lambda: self.set_status("Ready"))
        
    def _clear_chat(self):
        """Clear the chat display and reset conversation"""
        # Reset conversation history but keep system prompt
        self.messages = [self.messages[0]]
        self.conversation_count = 0
        
        # Clear the chat display
        self.message_frame.clear_messages()
        
        # Add welcome message
        self.message_frame.add_message(False, "Chat cleared. How can I help you today?")
        self.set_status("Ready")
        
    def set_status(self, status_text):
        """Set the status text"""
        self.status_var.set(status_text)
        self.update_idletasks()


def create_default_resources():
    """Create default resources if they don't exist"""
    # Create resources directory
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
            try:
                text_width = draw.textlength(text, font=font)
            except:
                # For older PIL versions
                text_width = draw.textsize(text, font=font)[0]
                
            text_height = 24  # Approximate height
            position = ((icon_size - text_width) // 2, (icon_size - text_height) // 2)
            
            # Draw text
            draw.text(position, text, fill=(255, 255, 255, 255), font=font)
            
            # Save
            icon_img.save(str(avatar_path), format='PNG')
        except Exception as e:
            print(f"Could not create AI avatar: {e}")


if __name__ == "__main__":
    try:
        # Ensure required packages
        try:
            import customtkinter
        except ImportError:
            print("Installing customtkinter package...")
            import subprocess
            subprocess.call([sys.executable, "-m", "pip", "install", "customtkinter"])
            import customtkinter
        
        # Create default resources
        create_default_resources()
        
        # Start the application
        app = ModernVoiceAssistantApp()
        app.mainloop()
    except Exception as e:
        # Show error in GUI if possible, otherwise fall back to console
        try:
            from tkinter import messagebox
            messagebox.showerror("Startup Error", f"An error occurred while starting the application: {e}")
        except:
            print(f"An error occurred while starting the application: {e}")
            import traceback
            traceback.print_exc()
