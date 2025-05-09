# Voice Conversation Assistant

A simplified voice conversation assistant that focuses on core functionality, providing both text-based and voice-based interaction modes.

## Features

- Dual-mode operation:
  - Text mode: Keyboard input with text output
  - Voice mode: Speech recognition input with voice output
- Speech-to-text conversion using ByteDance's ASR service
- Text-to-speech synthesis using ByteDance's TTS service
- Conversational AI using OpenAI/DeepSeek API
- Conversation history saving
- Organized media storage in data folder

## Project Structure

- `main.py` - Single entry point with both text and voice functionality
- `voice_assistant/` - Package containing core modules:
  - `ai_service.py` - AI conversation handling
  - `real_speech_to_text.py` - Voice input processing
  - `text_to_speech.py` - Voice output generation
  - Other supporting modules
- `data/` - Storage for generated media files and conversation logs
- `run_assistant.bat` - Windows batch file to easily run the application

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with the following variables (or copy from `.env.example`):
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   BASE_URL=your_base_url_here
   ASR_ACCESS_KEY=your_asr_access_key_here
   ASR_APP_KEY=your_asr_app_key_here
   TTS_ACCESS_TOKEN=your_tts_access_token_here
   TTS_APPID=your_tts_appid_here
   ```

## Running the Application

### Option 1: Using the batch file (Windows)

Simply double-click the `run_assistant.bat` file, which will:
- Install required dependencies
- Launch the application

### Option 2: Using Python directly

```
python main.py
```

## Usage

1. When the application starts, you'll be prompted to choose a mode:
   - Option 1: Text-based assistant (keyboard input/text output)
   - Option 2: Voice-based assistant (voice input/voice output)

2. For text mode:
   - Type your messages and press Enter
   - Read the AI's responses on screen
   - Conversation history is saved to the data folder

3. For voice mode:
   - Speak to the assistant when prompted
   - The assistant will respond with synthesized speech
   - Audio responses are saved in the data folder

4. In either mode, say or type "exit", "quit", "bye", or similar phrases to end the conversation

## Requirements

- Python 3.6 or later
- Windows, macOS, or Linux
- Microphone for voice input (voice mode only)
- Internet connection for API access

儿童陪伴故事语音助手
一款专为儿童设计的语音对话助手，可以讲故事、回答问题，提供温馨友好的交流体验。本项目专注于核心功能：语音输入、AI回应和语音输出，特别针对Windows系统优化。

🌟 特色功能

友好的橘色界面：专为儿童设计的温暖橘色调界面，视觉舒适
双重交互模式：
语音模式：说话即可得到AI回应，更自然流畅
文本模式：可以直接键盘输入，适合安静环境
即时语音中断：可随时打断AI回答开始新对话
Windows专用优化：针对Windows系统特别优化的语音识别
多重语音识别备选方案：
Google在线识别
离线识别
Windows原生语音识别
一键打包版本：无需安装Python，普通用户可直接使用

💻 适用场景

儿童睡前故事：温馨的故事陪伴，培养语言能力
知识问答：回答儿童好奇的各种问题
学习辅助：帮助解释课程内容，提供学习支持
休闲娱乐：与AI进行有趣互动，丰富儿童课余生活



📋 项目结构
  simple_assistant.py - 儿童友好的GUI语音助手（推荐使用）
  main.py - 命令行版语音对话助手
  voice_assistant/ - 核心功能模块：
  windows_speech.py - Windows专用语音识别
  ai_service.py - AI对话服务
  text_to_speech.py - 语音合成服务
  data/ - 生成的媒体文件和对话记录存储
  dist/语音助手.exe - 打包好的可执行文件，可直接运行
🚀 快速开始
  方法1：直接使用可执行文件（推荐）
  普通用户可以直接双击 dist/语音助手.exe 文件运行，无需任何安装步骤。

方法2：开发者使用Python运行
  安装依赖：

  pip install -r requirements.txt
  运行图形界面版本：

  python simple_assistant.py
  或运行命令行版本：

python main.py
🎯 使用指南
启动程序：

点击可执行文件或运行Python脚本
程序启动时会自动语音欢迎"你好，我是你的AI助手"
开始对话：

点击麦克风按钮开始语音输入
或在文本框中输入内容后发送
特殊功能：

语音播放时，可随时点击麦克风打断并开始新对话
点击"清空对话"可以重新开始新的对话
结束对话：

说或输入"退出"、"再见"等词语结束对话
🛠️ 开发者配置
配置环境变量（可选）： 在项目根目录创建 .env 文件，包含以下变量：

OPENAI_API_KEY=你的API密钥
打包成可执行文件：

python build_executable.py
🌐 系统要求
Windows 7/10/11 操作系统（推荐Windows 10或更高版本）
麦克风（用于语音输入）
扬声器（用于语音输出）
如使用Python版本：Python 3.6或更高版本
🙏 致谢
感谢所有开源语音识别和合成技术
感谢人工智能模型提供的对话能力
