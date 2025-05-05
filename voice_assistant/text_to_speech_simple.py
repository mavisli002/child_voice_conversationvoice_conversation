"""文本到语音转换模块 - 简化版"""
import os
import base64
import json
import uuid
import requests

def text_to_speech(text, output_file="response.mp3"):
    """
    将文本转换为语音并保存为MP3文件
    
    参数:
        text: 要转换的文本
        output_file: 输出文件名
        
    返回:
        bool: 成功返回True，失败返回False
    """
    # 从环境变量获取API凭证
    appid = os.getenv("TTS_APPID", "1787492884")
    access_token = os.getenv("TTS_ACCESS_TOKEN", "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_")
    cluster = "volcano_tts"
    voice_type = "BV001_streaming"  # 女声
    
    # API端点
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"
    
    # 请求头和请求体
    header = {"Authorization": f"Bearer;{access_token}"}
    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088"
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }
    
    try:
        # 发送请求到TTS API
        print("正在生成语音...")
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        
        # 检查响应是否包含数据
        if resp.status_code == 200 and "data" in resp.json():
            data = resp.json()["data"]
            
            # 将音频数据保存到文件
            with open(output_file, "wb") as file:
                file_content = base64.b64decode(data)
                file.write(file_content)
            
            print(f"语音已生成并保存到 {output_file}")
            return True
        else:
            print(f"生成语音时出错: {resp.text}")
            return False
    except Exception as e:
        print(f"语音生成过程中发生异常: {e}")
        return False


def play_audio(audio_file):
    """
    播放音频文件
    
    参数:
        audio_file: 音频文件路径
    """
    try:
        # 在Windows上使用默认播放器
        if os.name == 'nt':
            os.startfile(audio_file)
        # 在Linux上使用paplay
        elif os.name == 'posix':
            import subprocess
            subprocess.run(["paplay", audio_file])
        # 其他平台
        else:
            print(f"无法自动播放音频，请手动打开文件: {audio_file}")
    except Exception as e:
        print(f"播放音频时出错: {e}")
