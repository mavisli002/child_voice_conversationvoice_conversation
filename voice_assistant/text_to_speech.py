"""Text-to-speech module for voice assistant."""
import os
import base64
import json
import uuid
import requests
import pathlib
import io
import time


def split_text(text, max_length=100):
    """
    Split long text into chunks that won't exceed API limits.
    
    Args:
        text: The text to split
        max_length: Maximum length of each chunk
        
    Returns:
        list: List of text chunks
    """
    # Split by sentences to preserve meaning better
    sentences = []
    for paragraph in text.split('\n'):
        for sentence in paragraph.replace('。', '。|').replace('！', '！|').replace('？', '？|').replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|'):
            if sentence.strip():
                sentences.append(sentence.strip())
    
    # Group sentences into chunks
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed the limit, start a new chunk
        if len(current_chunk) + len(sentence) > max_length and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    # If still no chunks (could be a very short text), just use the original
    if not chunks and text.strip():
        chunks = [text.strip()]
        
    return chunks


def synthesize_single_chunk(chunk, api_url, headers, credentials):
    """
    Synthesize a single text chunk using the TTS API.
    
    Args:
        chunk: Text chunk to synthesize
        api_url: API endpoint URL
        headers: Request headers
        credentials: Dictionary with API credentials
        
    Returns:
        bytes: Audio data if successful, None otherwise
    """
    request_json = {
        "app": {
            "appid": credentials["appid"],
            "token": credentials["token"],
            "cluster": credentials["cluster"]
        },
        "user": {
            "uid": "388808087185088"
        },
        "audio": {
            "voice_type": credentials["voice_type"],
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": chunk,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }
    
    try:
        print(f"\nProcessing text chunk ({len(chunk)} characters)...")
        resp = requests.post(api_url, json.dumps(request_json), headers=headers)
        
        if resp.status_code == 200 and "data" in resp.json():
            data = resp.json()["data"]
            return base64.b64decode(data)
        else:
            print(f"\nFailed to process text chunk: {resp.text}")
            print(f"\n!! 处理文本块失败: {resp.text}")
            return None
    except Exception as e:
        print(f"\n!! 处理文本块时出错: {e}")
        return None


def synthesize_speech(text, output_filename):
    """
    Convert text to speech using ByteDance TTS API.
    
    Args:
        text: The text to convert to speech
        output_filename: The filename to save the audio to
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get API credentials from environment variables
    credentials = {
        "appid": os.getenv("TTS_APPID", "1787492884"),
        "token": os.getenv("TTS_ACCESS_TOKEN", "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_"),
        "cluster": "volcano_tts",
        "voice_type": "BV001_streaming"
    }
    
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"
    headers = {"Authorization": f"Bearer;{credentials['token']}"}
    
    # Ensure data directory exists
    data_dir = pathlib.Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create full path for output file
    output_path = data_dir / output_filename
    
    # Clean the text (remove excess whitespace)
    text = " ".join(text.split())
    
    # For very long responses, we need to split them
    text_chunks = split_text(text)
    if len(text_chunks) > 1:
        print(f"\n>> 文本较长 ({len(text)}字符)，已分为 {len(text_chunks)} 个部分处理")
    
    # Process text chunks and combine them
    if len(text_chunks) > 1:
        # For multiple chunks, process each one and combine the audio
        chunk_audio_data = []
        success = True
        
        for i, chunk in enumerate(text_chunks):
            print(f"\n>> 处理第 {i+1}/{len(text_chunks)} 块...")
            audio_data = synthesize_single_chunk(chunk, api_url, headers, credentials)
            
            if audio_data:
                chunk_audio_data.append(audio_data)
            else:
                print(f"\n!! 第 {i+1} 块文本处理失败，尝试简化文本...")
                # Try with even smaller chunks
                smaller_chunks = split_text(chunk, max_length=50)
                for j, smaller_chunk in enumerate(smaller_chunks):
                    sub_audio = synthesize_single_chunk(smaller_chunk, api_url, headers, credentials)
                    if sub_audio:
                        chunk_audio_data.append(sub_audio)
                    else:
                        success = False
                        print(f"\n!! 无法处理部分文本，已跳过")
        
        # Combine all audio chunks if we have any
        if chunk_audio_data:
            print(f"\n>> 正在合并 {len(chunk_audio_data)} 个音频块...")
            try:
                # Write all audio data to the output file
                with open(output_path, "wb") as outfile:
                    for audio_data in chunk_audio_data:
                        outfile.write(audio_data)
                        
                print(f"\n√√ 语音合成完成，已保存至 {output_path}")
                return True
            except Exception as e:
                print(f"\n!! 合并音频时出错: {e}")
                return False
        else:
            print("\n!! 没有成功生成任何音频块")
            return False
    else:
        # For a single chunk, just process directly
        print("\n>> 处理文本...")
        audio_data = synthesize_single_chunk(text_chunks[0], api_url, headers, credentials)
        
        if audio_data:
            try:
                # Write audio data to the output file
                with open(output_path, "wb") as outfile:
                    outfile.write(audio_data)
                print(f"\n√√ 语音合成完成，已保存至 {output_path}")
                return True
            except Exception as e:
                print(f"\n!! 保存音频时出错: {e}")
                return False
        else:
            print("\n!! 文本处理失败")
            return False


