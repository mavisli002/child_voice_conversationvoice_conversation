"""
Voice Conversation Assistant
-------------------------------------------
A simplified voice conversation assistant focused on core functionality:
1. Voice/Text input
2. AI processing
3. Voice/Text output

This script provides both text-based and voice-based conversation modes.
"""
import os
import sys
import io
import time
import pathlib
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


def run_voice_assistant(system_prompt="你是一个有帮助的助手"):
    """Run the voice-based assistant with voice input and output."""
    messages = [{"role": "system", "content": system_prompt}]
    
    count = 0
    EXIT_PHRASES = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}
    
    print("=" * 50)
    print("语音对话助手 (Voice Conversation Assistant)")
    print("=" * 50)
    print("提示: 系统将提示您开始说话，请在提示后对着麦克风说话")
    print("      当您说话时，屏幕将显示“正在倒听”状态")
    print("      如果语音识别失败，您可以直接输入文字")
    print("      说'退出'或'exit'结束对话")
    print("=" * 50)
    
    try:
        while True:
            count += 1
            print("\n" + "-" * 40)
            print(f"[对话 #{count}]")
            print("-" * 40)
            print("\n• 准备开始...")
            print("\n🎤 请开始说话 (系统将自动检测您何时开始说话)")
            
            # Try to get speech input with a timeout
            try:
                user_text = record_and_transcribe(duration=5, language="zh-CN")
            except Exception as e:
                print(f"\n❌ 语音识别出错: {e}")
                user_text = ""
                
            # If speech recognition failed, fall back to text input
            if not user_text:
                print("\n❌ 未能识别语音，请直接输入文字:")
                try:
                    print("⌨️ > ", end="")
                    user_text = input()
                except (EOFError, KeyboardInterrupt):
                    print("\n❌ 用户终止，退出")
                    break
                    
                if not user_text:
                    print("\n❌ 未获取到输入，请重试")
                    continue
                
            print(f"\n🗣 您说: {user_text}")
            
            # Check if user wants to exit
            if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
                print("\n🚫 检测到退出指令，结束对话")
                break
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Generate AI response
            start_time = time.time()
            print("\n🤖 AI正在思考...", end="", flush=True)
            
            # Start generating response with animation
            animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            i = 0
            is_generating = True
            
            # Define a function to generate response
            def generate():
                nonlocal is_generating
                response = generate_response(messages)
                is_generating = False
                return response
                
            # Start generating in a separate thread if threading is available
            try:
                import threading
                thread = threading.Thread(target=lambda: globals().update({'ai_response': generate()}))
                thread.daemon = True
                thread.start()
                
                # Show animation while generating
                while is_generating and thread.is_alive():
                    print(f"\rAI正在思考... {animation[i % len(animation)]}", end="", flush=True)
                    time.sleep(0.1)
                    i += 1
                thread.join()
                ai_response = globals().get('ai_response', '')
            except (ImportError, RuntimeError):
                # Fallback if threading is not available
                ai_response = generate_response(messages)
                is_generating = False
            
            # Calculate thinking time
            thinking_time = time.time() - start_time
            print(f"\rAI已完成思考 ({thinking_time:.1f}秒)" + " "*30)
            
            # Display the response with proper formatting
            print(f"\n>> 助手回复: {ai_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
            
            # Convert AI response to speech
            print("\n>> 正在生成语音回复...")
            mp3_filename = f"response_{count}.mp3"
            
            # Track TTS start time
            tts_start = time.time()
            success = synthesize_speech(ai_response, mp3_filename)
            tts_time = time.time() - tts_start
            
            if success:
                print(f"\n√√ 语音生成完成 ({tts_time:.1f}秒)")
            else:
                print("\n!! 语音生成可能不完整，但将尝试播放可用部分")
            
            # Play the generated speech
            try:
                # For Windows, use the default player
                audio_path = pathlib.Path("data") / mp3_filename
                
                if os.path.exists(audio_path):
                    print(f"\n>> 正在播放语音回复...")
                os.startfile(audio_path)
                
                # Wait for audio to finish (approximate)
                words_per_second = 2.5  # Estimated speaking rate
                wait_time = min(len(ai_response.split()) / words_per_second, 30)  # Cap at 30 seconds
                
                # Simple progress indicator
                for i in range(int(wait_time)):
                    print(".", end="", flush=True)
                    time.sleep(1)
                print("\n\n✅ 语音回复已播放完毕")  
                
            except AttributeError:
                # Fallback for non-Windows platforms
                if os.name == 'posix':
                    import subprocess
                    audio_path = pathlib.Path("data") / mp3_filename
                    print(f"\n>> 正在播放语音回复...")
                    subprocess.run(["paplay", audio_path])
                    print("\n✅ 语音回复已播放完毕")
                else:
                    print(f"\n💾 语音文件已保存至 data/{mp3_filename}")
                    print("请手动打开文件收听回复")
    
    except KeyboardInterrupt:
        print("\n用户终止，退出")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 50)
        print("语音助手已关闭")
        print("=" * 50)


def run_text_assistant(system_prompt="你是一个有帮助的助手", save_conversation=True):
    """Run the text-based assistant with text input and output."""
    # Initialize conversation
    messages = [{"role": "system", "content": system_prompt}]
    
    # Default exit phrases
    exit_phrases = {"结束", "退出", "拜拜", "再见", "break out", "bye", "exit", "quit"}
    
    count = 0
    conversation_log = []
    
    print("===== 文本助手已启动，请开始对话 =====")
    print("使用文本输入模式")
    print(f"输入以下任意词语结束对话: {', '.join(exit_phrases)}")
    
    try:
        while True:
            count += 1
            print("\n等待用户输入...")
            
            # Get user input (text only)
            print("> ", end="")
            user_text = input()
            if not user_text:
                print("未获取到输入，请重试")
                continue
                
            print(f"用户: {user_text}")
            
            # Save to conversation log
            if save_conversation:
                conversation_log.append(f"用户: {user_text}")
            
            # Check if user wants to exit
            if any(exit_phrase in user_text.lower() for exit_phrase in exit_phrases):
                print("检测到退出指令，结束对话")
                break
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Generate AI response
            print("AI正在思考...")
            ai_response = generate_response(messages)
            print(f"助手: {ai_response}")
            
            # Save to conversation log
            if save_conversation:
                conversation_log.append(f"助手: {ai_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
    
    except KeyboardInterrupt:
        print("\n用户终止，退出")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("语音助手已关闭")
        
        # Save conversation history if enabled
        if save_conversation and conversation_log:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"
            
            # Ensure data directory exists
            data_dir = pathlib.Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Save to data directory
            file_path = data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(conversation_log))
            print(f"对话历史已保存至 {file_path}")


def main():
    """Main entry point with mode selection."""
    print("=" * 50)
    print("语音对话助手 (Voice Conversation Assistant)")
    print("=" * 50)
    print("请选择模式:")
    print("1. 文本模式 (键盘输入/文本输出)")
    print("2. 语音模式 (语音输入/语音输出)")
    print("=" * 50)
    
    choice = input("请输入选择 (1 或 2): ")
    
    if choice == "1":
        run_text_assistant(system_prompt="你是一个有帮助的助手，请简洁明了地回答问题")
    elif choice == "2":
        run_voice_assistant(system_prompt="你是一个有帮助的助手，请简洁明了地回答问题")
    else:
        print("无效选择，请重新运行程序并选择 1 或 2")

    print("      输入'退出'或'exit'结束对话")
    
    try:
        while True:
            count += 1
            print("\n等待用户输入...")
            
            # Get speech input and convert to text
            user_text = record_and_transcribe()
            if not user_text:
                print("未能识别语音，请重试")
                continue
                
            print(f"用户: {user_text}")
            
            # Check if user wants to exit
            if any(exit_phrase in user_text.lower() for exit_phrase in EXIT_PHRASES):
                print("检测到退出指令，结束对话")
                break
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Generate AI response
            print("AI正在思考...")
            ai_response = generate_response(messages)
            print(f"助手: {ai_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
            
            # Convert AI response to speech
            print("生成语音回复...")
            mp3_filename = f"response_{count}.mp3"
            synthesize_speech(ai_response, mp3_filename)
            
            # Play the generated speech
            try:
                # For Windows, use the default player
                os.startfile(pathlib.Path(mp3_filename))
            except AttributeError:
                # Fallback for non-Windows platforms
                if os.name == 'posix':
                    subprocess.run(["paplay", pathlib.Path(mp3_filename)])
                else:
                    print(f"Generated speech saved to {mp3_filename}")
                    print("Please open the file manually to hear the response.")
    
    except KeyboardInterrupt:
        print("\n用户终止，退出")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("语音助手已关闭")

if __name__ == "__main__":
    main()
