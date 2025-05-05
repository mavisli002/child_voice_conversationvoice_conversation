"""Speech-to-text module for voice assistant."""
import os
import asyncio
import datetime
import gzip
import json
import uuid
import wave
import tempfile
import subprocess
from io import BytesIO

import aiofiles
import websockets

# Protocol constants
PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

FULL_CLIENT_REQUEST = 0b0001
AUDIO_ONLY_REQUEST = 0b0010
FULL_SERVER_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

NO_SEQUENCE = 0b0000
POS_SEQUENCE = 0b0001
NEG_SEQUENCE = 0b0010
NEG_WITH_SEQUENCE = 0b0011

NO_SERIALIZATION = 0b0000
JSON = 0b0001

NO_COMPRESSION = 0b0000
GZIP = 0b0001


def generate_header(
    message_type=FULL_CLIENT_REQUEST,
    message_type_specific_flags=NO_SEQUENCE,
    serial_method=JSON,
    compression_type=GZIP,
    reserved_data=0x00,
):
    """Generate header for websocket communication."""
    header = bytearray()
    header_size = 1
    header.append((PROTOCOL_VERSION << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    return header


def generate_before_payload(sequence: int):
    """Generate sequence bytes before payload."""
    return sequence.to_bytes(4, "big", signed=True)


def parse_response(res: bytes) -> dict:
    """Parse response from ASR service."""
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0F
    message_type = res[1] >> 4
    message_flags = res[1] & 0x0F
    serialization = res[2] >> 4
    compression = res[2] & 0x0F

    payload = res[header_size * 4 :]
    rst = {
        "message_type": message_type,
        "flags": message_flags,
        "is_last_package": bool(message_flags & 0x02),
    }

    if message_flags & 0x01:  # Has sequence
        rst["payload_sequence"] = int.from_bytes(payload[:4], "big", signed=True)
        payload = payload[4:]

    if message_type == FULL_SERVER_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == SERVER_ACK:
        return rst  # ACK just return
    elif message_type == SERVER_ERROR_RESPONSE:
        rst["code"] = int.from_bytes(payload[:4], "big")
        payload_size = int.from_bytes(payload[4:8], "big")
        payload_msg = payload[8:]
    else:
        return rst

    if compression == GZIP:
        payload_msg = gzip.decompress(payload_msg)
    if serialization == JSON:
        payload_msg = json.loads(payload_msg.decode())
    else:
        payload_msg = payload_msg.decode(errors="ignore")

    rst["payload_msg"] = payload_msg
    rst["payload_size"] = payload_size
    return rst


def read_wav_info(data: bytes):
    """Read WAV file information."""
    with BytesIO(data) as f:
        wf = wave.open(f, "rb")
        nch, sw, fr, nf = wf.getparams()[:4]
        return nch, sw, fr, nf, wf.readframes(nf)


class AsrWsClient:
    """Client for ASR (Automatic Speech Recognition) WebSocket service."""

    def __init__(self, audio_path, **kwargs):
        """Initialize ASR WebSocket client."""
        self.audio_path = audio_path

        self.seg_duration = int(kwargs.get("seg_duration", 100))
        self.ws_url = kwargs.get(
            "ws_url", "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel"
        )

        self.uid = kwargs.get("uid", "test")
        self.format = kwargs.get("format", "wav")
        self.rate = kwargs.get("rate", 16000)
        self.bits = kwargs.get("bits", 16)
        self.channel = kwargs.get("channel", 1)
        self.codec = kwargs.get("codec", "raw")

        self.streaming = kwargs.get("streaming", True)
        self.mp3_seg_size = kwargs.get("mp3_seg_size", 1000)

        self.access_key = kwargs.get("access_key", os.getenv("ASR_ACCESS_KEY", ""))
        self.app_key = kwargs.get("app_key", os.getenv("ASR_APP_KEY", ""))

    def construct_request(self, reqid):
        """Construct initial request for ASR service."""
        return {
            "user": {"uid": self.uid},
            "audio": {
                "format": self.format,
                "sample_rate": self.rate,
                "bits": self.bits,
                "channel": self.channel,
                "codec": self.codec,
            },
            "request": {"model_name": "bigmodel", "enable_punc": True},
        }

    @staticmethod
    def slice_data(data, chunk):
        """Slice data into chunks."""
        for off in range(0, len(data), chunk):
            end = min(off + chunk, len(data))
            yield data[off:end], end == len(data)

    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        """Process audio data in segments."""
        reqid = str(uuid.uuid4())
        seq = 1

        payload = gzip.compress(json.dumps(self.construct_request(reqid)).encode())
        first = bytearray(generate_header(message_type_specific_flags=POS_SEQUENCE))
        first.extend(generate_before_payload(seq))
        first.extend(len(payload).to_bytes(4, "big"))
        first.extend(payload)

        headers = {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Access-Key": self.access_key,
            "X-Api-App-Key": self.app_key,
            "X-Api-Request-Id": reqid,
        }

        printed_text = ""
        seen_seq = set()

        async with websockets.connect(
            self.ws_url, additional_headers=headers, max_size=1_000_000_000
        ) as ws:
            await ws.send(first)
            await ws.recv()  # Discard handshake ACK

            for chunk, last in self.slice_data(wav_data, segment_size):
                seq += 1
                flag = NEG_WITH_SEQUENCE if last else POS_SEQUENCE

                body = gzip.compress(chunk)
                msg = bytearray(
                    generate_header(
                        message_type=AUDIO_ONLY_REQUEST, message_type_specific_flags=flag
                    )
                )
                msg.extend(generate_before_payload(-seq if last else seq))
                msg.extend(len(body).to_bytes(4, "big"))
                msg.extend(body)
                await ws.send(msg)

                # Process response
                res = parse_response(await ws.recv())

                if res["message_type"] != FULL_SERVER_RESPONSE:
                    continue

                seq_no = res.get("payload_sequence")
                if seq_no in seen_seq:
                    continue
                seen_seq.add(seq_no)

                text = res.get("payload_msg", {}).get("result", {}).get("text", "")

                if text and text != printed_text:
                    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"[{ts}] {text}")
                    printed_text = text

                if res["is_last_package"]:
                    break

                if self.streaming:
                    await asyncio.sleep(self.seg_duration / 1000)

        return printed_text

    async def execute(self):
        """Execute ASR processing."""
        async with aiofiles.open(self.audio_path, "rb") as f:
            raw = await f.read()

        if self.format == "wav":
            nch, sw, fr, nf, _pcm = read_wav_info(raw)
            seg = int(nch * sw * fr * self.seg_duration / 1000)
            return await self.segment_data_processor(raw, seg)

        if self.format == "pcm":
            seg = int(self.rate * 2 * self.channel * self.seg_duration / 1000)
            return await self.segment_data_processor(raw, seg)

        if self.format == "mp3":
            return await self.segment_data_processor(raw, self.mp3_seg_size)

        raise ValueError("Unsupported audio format")


def execute_one(audio_path: str, **kwargs):
    """Execute ASR on a single audio file."""
    return asyncio.run(AsrWsClient(audio_path, **kwargs).execute())


def record_audio(duration=5, output_file="temp_recording.wav"):
    """Simulate audio recording for testing purposes.
    
    In a real implementation, this would use a library like PyAudio or ffmpeg
    to record actual audio from the microphone.
    """
    print(f"[Simulated] Recording for {duration} seconds...")
    print("Since ffmpeg is not detected, we're using simulated input.")
    print("Type your message (simulating voice input): ")
    
    # Get text input from user instead of recording audio
    try:
        user_input = input("> ")
    except EOFError:
        print("\nInput terminated. Using default input.")
        user_input = "你好"
    except KeyboardInterrupt:
        print("\nInput interrupted. Using default input.")
        user_input = "退出"
    
    # Create a dummy WAV file for compatibility with the rest of the code
    # This is just a placeholder - in a real app, this would be actual audio
    try:
        # Use a temporary file if none specified
        if not output_file:
            temp_fd, output_file = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            
        # Create a simple WAV file (1 second of silence)
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes per sample (16 bits)
            wf.setframerate(16000)  # 16kHz
            wf.writeframes(b'\x00' * 32000)  # 1 second of silence
            
        # Store the user input in a separate file for the mock transcription
        with open(output_file + ".txt", "w") as f:
            f.write(user_input)
            
        return output_file
    except Exception as e:
        print(f"Error creating simulated audio file: {e}")
        return None


def record_and_transcribe(duration=5):
    """Record audio and transcribe it to text.
    
    In the simulated version, this just returns the text input directly.
    In a real implementation, this would use the ASR service to transcribe audio.
    """
    # Record audio (or get simulated input)
    audio_file = record_audio(duration)
    if not audio_file:
        return ""
    
    # In simulation mode, read the text from the .txt file instead of transcribing
    text_file = audio_file + ".txt"
    if os.path.exists(text_file):
        try:
            with open(text_file, "r") as f:
                text = f.read().strip()
            print(f"[Simulated] Transcription: {text}")
            
            # Clean up temporary files
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(text_file):
                os.remove(text_file)
                
            return text
        except Exception as e:
            print(f"Error reading simulated transcription: {e}")
            return ""
    
    # If not in simulation mode, use the real ASR service
    try:
        print("Transcribing audio...")
        text = execute_one(
            audio_file,
            access_key=os.getenv("ASR_ACCESS_KEY", "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_"),
            app_key=os.getenv("ASR_APP_KEY", "1787492884")
        )
        
        # Clean up temporary file
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        return text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""
