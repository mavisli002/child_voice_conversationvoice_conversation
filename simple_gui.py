#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版语音对话助手GUI入口
专为Windows系统优化，解决闪退问题
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
import platform

def main():
    try:
        # 确保数据目录存在
        os.makedirs("data/resources", exist_ok=True)
        
        # 导入必要库
        import customtkinter as ctk
        from PIL import Image, ImageTk
        
        # 设置外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        app = ctk.CTk()
        app.title("语音对话助手")
        app.geometry("800x600")
        
        # 设置中文字体
        font_family = "Microsoft YaHei UI" if os.name == "nt" else "PingFang SC"
        default_font = (font_family, 12)
        title_font = (font_family, 16, "bold")
        
        # 创建标题
        title_label = ctk.CTkLabel(app, text="语音对话助手", font=title_font)
        title_label.pack(pady=20)
        
        # 创建内容区域
        frame = ctk.CTkFrame(app)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 欢迎消息
        info_label = ctk.CTkLabel(
            frame, 
            text="欢迎使用语音对话助手！\n正在加载界面...", 
            font=default_font,
            wraplength=700
        )
        info_label.pack(pady=20)
        
        # 导入语音助手模块并启动完整界面
        def load_full_gui():
            app.withdraw()  # 隐藏当前窗口
            
            try:
                # 导入完整GUI
                from chatgpt_style_gui import ChatGPTWindow
                
                # 启动完整GUI
                full_app = ChatGPTWindow()
                full_app.mainloop()
                
                # 如果完整GUI关闭，则退出程序
                app.destroy()
                
            except Exception as e:
                # 显示错误信息并恢复简易界面
                app.deiconify()
                error_msg = f"加载完整界面时出错: {str(e)}"
                messagebox.showerror("错误", error_msg)
                info_label.configure(text=f"出现错误: {str(e)}\n\n请确保已正确安装所有依赖:\npip install customtkinter pillow python-dotenv speech_recognition")
        
        # 使用按钮手动加载完整界面
        load_button = ctk.CTkButton(
            frame, 
            text="启动完整界面", 
            font=default_font,
            command=load_full_gui
        )
        load_button.pack(pady=20)
        
        # 在延迟后自动加载完整界面
        app.after(1500, load_full_gui)
        
        # 运行简易界面
        app.mainloop()
        
    except Exception as e:
        # 显示错误对话框
        try:
            messagebox.showerror("启动错误", f"程序启动时发生错误: {str(e)}")
        except:
            print(f"程序启动时发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
