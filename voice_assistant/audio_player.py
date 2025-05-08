"""
音频播放器模块 - 使用Windows本地音频库在程序内播放音频
"""
import os
import threading
import time
import platform

class AudioPlayer:
    """在GUI应用中直接播放音频的播放器类"""
    
    def __init__(self):
        """初始化音频播放器"""
        self.is_playing = False
        self.play_thread = None
        self.current_process = None
        
    def play(self, audio_file, callback=None):
        """
        播放音频文件
        
        参数:
            audio_file: 音频文件路径
            callback: 播放结束后的回调函数
        
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            # 确保文件存在
            if not os.path.exists(audio_file):
                print(f"错误: 音频文件不存在: {audio_file}")
                return False
                
            # 停止当前正在播放的声音
            self.stop()
            
            # 使用Windows的winsound播放音频
            if platform.system() == 'Windows':
                import winsound
                
                # 标记为正在播放
                self.is_playing = True
                
                # 在单独的线程中播放音频
                def play_in_thread():
                    try:
                        # 播放音频 (SND_FILENAME 表示使用文件名，SND_ASYNC 表示异步播放，SND_NODEFAULT 防止弹出播放器窗口)
                        flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                        winsound.PlaySound(audio_file, flags)
                        
                        # 估算播放时间
                        file_size = os.path.getsize(audio_file)
                        # 估算MP3播放时间
                        estimated_seconds = file_size / (44100 * 2)
                        wait_time = max(1, min(estimated_seconds, 30))
                        time.sleep(wait_time)
                        
                        # 播放结束后更新状态
                        self.is_playing = False
                        
                        # 回调函数
                        if callback:
                            callback()
                    except Exception as e:
                        print(f"播放线程中发生错误: {e}")
                        self.is_playing = False
                        if callback:
                            callback()
                
                # 启动线程
                self.play_thread = threading.Thread(target=play_in_thread)
                self.play_thread.daemon = True
                self.play_thread.start()
                
                return True
            else:
                print("不支持的平台，只能在Windows上使用")
                return False
            
        except Exception as e:
            print(f"播放音频时出错: {e}")
            self.is_playing = False
            return False
    
    def stop(self):
        """停止当前播放的音频"""
        if not self.is_playing:
            return
            
        try:
            if platform.system() == 'Windows':
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.is_playing = False
        except Exception as e:
            print(f"停止音频时出错: {e}")
        
    def is_busy(self):
        """
        检查是否正在播放音频
        
        返回:
            bool: 正在播放返回True，否则返回False
        """
        return self.is_playing

# 全局音频播放器实例
player = AudioPlayer()

def play_audio(audio_file, callback=None):
    """
    便捷函数：播放音频文件
    
    参数:
        audio_file: 音频文件路径
        callback: 播放结束后的回调函数
    
    返回:
        bool: 成功返回True，失败返回False
    """
    return player.play(audio_file, callback)

def stop_audio():
    """停止当前播放的所有音频"""
    player.stop()
