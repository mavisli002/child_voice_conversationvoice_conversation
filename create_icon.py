"""
创建一个简单的麦克风图标作为应用程序图标
"""
import os
from PIL import Image, ImageDraw

# 创建一个简单的麦克风图标
def create_microphone_icon(filename="voice_icon.ico", size=256):
    # 创建一个透明背景
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    bg_color = (255, 102, 0)  # 橙色
    draw.ellipse((10, 10, size-10, size-10), fill=bg_color)
    
    # 麦克风主体
    mic_color = (255, 255, 255)  # 白色
    mic_top = size//4
    mic_bottom = 3*size//4
    mic_left = size//3
    mic_right = 2*size//3
    
    # 绘制麦克风长方体
    draw.rectangle((mic_left, mic_top, mic_right, mic_bottom), fill=mic_color)
    draw.ellipse((mic_left, mic_top-10, mic_right, mic_top+10), fill=mic_color)
    
    # 绘制麦克风底座
    stand_top = mic_bottom
    stand_bottom = mic_bottom + size//8
    stand_width = size//8
    draw.rectangle((size//2 - stand_width//2, stand_top, 
                   size//2 + stand_width//2, stand_bottom), fill=mic_color)
    
    # 绘制底座
    base_top = stand_bottom - 5
    base_bottom = stand_bottom + 5
    base_width = size//3
    draw.rectangle((size//2 - base_width//2, base_top,
                   size//2 + base_width//2, base_bottom), fill=mic_color)
    
    # 保存为ICO格式
    img.save(filename, format='ICO')
    print(f"图标已创建: {filename}")
    return os.path.abspath(filename)

if __name__ == "__main__":
    create_microphone_icon()
