"""
打包脚本 - 将简易语音助手打包为可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

print("=" * 60)
print("正在准备打包语音助手为可执行文件...")
print("=" * 60)

# 确保data目录存在
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 准备额外的数据文件
extra_datas = [
    ("voice_assistant", "voice_assistant"),  # 包含所有语音助手模块
    ("data", "data"),  # 包含所有数据文件
]

# 准备隐藏导入的模块
hidden_imports = [
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
    "pygame",
    "customtkinter",
    "speech_recognition",
    "openai",
    "dotenv",
]

# 构建命令行参数
pyinstaller_args = [
    "pyinstaller",
    "--name=语音助手",
    "--windowed",  # 使用GUI模式，不显示控制台
    "--onefile",   # 打包成单个文件
    "--icon=voice_icon.ico" if os.path.exists("voice_icon.ico") else "",  # 如果有图标则使用
    "--clean",     # 清理临时文件
    "--noconfirm"  # 不要询问确认
]

# 添加额外的数据文件
for src, dst in extra_datas:
    if os.path.exists(src):
        pyinstaller_args.append(f"--add-data={src};{dst}")

# 添加隐藏导入
for imp in hidden_imports:
    pyinstaller_args.append(f"--hidden-import={imp}")

# 添加主脚本
pyinstaller_args.append("simple_assistant.py")

# 过滤掉空字符串
pyinstaller_args = [arg for arg in pyinstaller_args if arg]

print("执行打包命令:", " ".join(pyinstaller_args))
print("-" * 60)

# 执行PyInstaller命令
try:
    subprocess.run(pyinstaller_args, check=True)
    print("=" * 60)
    print("打包完成!")
    print("可执行文件位于: dist/语音助手.exe")
    print("=" * 60)
except subprocess.CalledProcessError as e:
    print(f"打包过程中出错: {e}")
    sys.exit(1)

# 创建一个快捷方式批处理文件，方便用户使用
with open("启动语音助手.bat", "w", encoding="utf-8") as f:
    f.write("@echo off\n")
    f.write("echo 正在启动语音助手...\n")
    f.write("start dist\\语音助手.exe\n")

print("已创建启动批处理文件: 启动语音助手.bat")
