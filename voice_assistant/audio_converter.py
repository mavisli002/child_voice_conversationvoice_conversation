"""Audio conversion utilities for voice assistant."""
import os
import subprocess
import tempfile
from pathlib import Path


class AudioConverter:
    """Class for handling audio format conversions."""
    
    @staticmethod
    def convert_audio(input_file, output_format="mp3", output_file=None, **kwargs):
        """
        Convert audio file to specified format.
        
        Args:
            input_file (str): Path to input audio file
            output_format (str): Desired output format (mp3, wav, ogg, etc.)
            output_file (str, optional): Path to output file. If None, generates a name.
            **kwargs: Additional conversion parameters
                - sample_rate: Sample rate in Hz (e.g., 16000, 44100)
                - channels: Number of audio channels (1=mono, 2=stereo)
                - bit_depth: Bit depth (8, 16, 24, 32)
                - bitrate: Bitrate for compressed formats (e.g., "128k")
        
        Returns:
            str: Path to converted audio file, or None if conversion failed
        """
        # Generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix(f".{output_format}"))
        
        # Check if ffmpeg is available
        try:
            # Try to use ffmpeg for conversion
            cmd = ["ffmpeg", "-y", "-i", input_file]
            
            # Add conversion parameters if provided
            if "sample_rate" in kwargs:
                cmd.extend(["-ar", str(kwargs["sample_rate"])])
            if "channels" in kwargs:
                cmd.extend(["-ac", str(kwargs["channels"])])
            if "bitrate" in kwargs and output_format in ["mp3", "ogg"]:
                cmd.extend(["-b:a", kwargs["bitrate"]])
                
            # Add output file
            cmd.append(output_file)
            
            # Run conversion
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return output_file
        except (subprocess.SubprocessError, FileNotFoundError):
            print("ffmpeg not available, using fallback conversion method")
            return AudioConverter._fallback_convert(input_file, output_format, output_file, **kwargs)
    
    @staticmethod
    def _fallback_convert(input_file, output_format, output_file, **kwargs):
        """
        Fallback conversion method using Python libraries.
        
        This is used when ffmpeg is not available.
        """
        try:
            import wave
            from pydub import AudioSegment
            
            # Use pydub for conversion
            if Path(input_file).suffix.lower() == ".wav" and output_format.lower() == "mp3":
                sound = AudioSegment.from_wav(input_file)
                sound.export(output_file, format="mp3", bitrate=kwargs.get("bitrate", "128k"))
                return output_file
            elif Path(input_file).suffix.lower() == ".mp3" and output_format.lower() == "wav":
                sound = AudioSegment.from_mp3(input_file)
                sound.export(
                    output_file, 
                    format="wav", 
                    parameters=[
                        "-ar", str(kwargs.get("sample_rate", 44100)),
                        "-ac", str(kwargs.get("channels", 1))
                    ]
                )
                return output_file
            else:
                print(f"Unsupported conversion: {Path(input_file).suffix} to {output_format}")
                return None
        except ImportError:
            print("pydub not available for fallback conversion")
            return None

    @staticmethod
    def text_to_speech(text, output_file=None, voice_type="female", language="zh"):
        """
        Convert text to speech using the TTS module.
        
        This is a convenience wrapper around the TTS functionality.
        
        Args:
            text (str): Text to convert to speech
            output_file (str, optional): Path to output file. If None, generates a temp file.
            voice_type (str): Voice type (male, female)
            language (str): Language code (en, zh, etc.)
            
        Returns:
            str: Path to generated audio file
        """
        from voice_assistant.text_to_speech import synthesize_speech
        
        # Generate output filename if not provided
        if output_file is None:
            temp_fd, output_file = tempfile.mkstemp(suffix=".mp3")
            os.close(temp_fd)
        
        # Call the TTS function
        success = synthesize_speech(text, output_file)
        
        if success:
            return output_file
        return None
    
    @staticmethod
    def speech_to_text(audio_file, language="zh"):
        """
        Convert speech to text using the STT module.
        
        This is a convenience wrapper around the STT functionality.
        
        Args:
            audio_file (str): Path to audio file
            language (str): Language code (en, zh, etc.)
            
        Returns:
            str: Transcribed text
        """
        from voice_assistant.speech_to_text import execute_one
        
        try:
            # Call the STT function
            text = execute_one(
                audio_file,
                access_key=os.getenv("ASR_ACCESS_KEY", "j-akE7AtBfD1Erx0Ad9lDmX7o5lMfuY_"),
                app_key=os.getenv("ASR_APP_KEY", "1787492884")
            )
            return text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""


# Utility functions for common conversions
def wav_to_mp3(wav_file, mp3_file=None, bitrate="192k"):
    """Convert WAV to MP3."""
    return AudioConverter.convert_audio(
        wav_file, 
        output_format="mp3", 
        output_file=mp3_file,
        bitrate=bitrate
    )

def mp3_to_wav(mp3_file, wav_file=None, sample_rate=16000, channels=1):
    """Convert MP3 to WAV."""
    return AudioConverter.convert_audio(
        mp3_file, 
        output_format="wav", 
        output_file=wav_file,
        sample_rate=sample_rate,
        channels=channels
    )

def generate_speech(text, output_file=None):
    """Generate speech from text."""
    return AudioConverter.text_to_speech(text, output_file)

def transcribe_audio(audio_file):
    """Transcribe audio to text."""
    return AudioConverter.speech_to_text(audio_file)
