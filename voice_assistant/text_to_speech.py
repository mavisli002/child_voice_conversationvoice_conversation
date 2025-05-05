"""Text-to-speech module for voice assistant."""
import os
import base64
import json
import uuid
import requests
import pathlib


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
    appid = os.getenv("TTS_APPID", "1787492884")
    access_token = os.getenv("TTS_ACCESS_TOKEN", "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_")
    cluster = "volcano_tts"
    voice_type = "BV001_streaming"
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"

    # Set up request headers and body
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
        # Send request to TTS API
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        
        # Check if response contains data
        if resp.status_code == 200 and "data" in resp.json():
            data = resp.json()["data"]
            
            # Ensure data directory exists
            data_dir = pathlib.Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Create full path for output file
            output_path = data_dir / output_filename
            
            # Save audio data to file
            with open(output_path, "wb") as file_to_save:
                file_to_save.write(base64.b64decode(data))
            
            print(f"Speech synthesized and saved to {output_path}")
            return True
        else:
            print(f"Error synthesizing speech: {resp.text}")
            return False
    except Exception as e:
        print(f"Exception during speech synthesis: {e}")
        return False
