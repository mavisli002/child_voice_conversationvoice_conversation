"""AI服务模块 - 简化版"""
import os
from openai import OpenAI

def generate_response(messages):
    """
    生成AI回复
    
    参数:
        messages: 消息历史列表，每个消息包含'role'和'content'键
        
    返回:
        str: 生成的回复文本
    """
    try:
        # 使用环境变量中的API密钥和基础URL初始化OpenAI客户端
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), 
            base_url=os.getenv("BASE_URL", "https://api.deepseek.com")
        )
        
        # 创建聊天完成
        print("正在生成AI回复...")
        response = client.chat.completions.create(
            model="deepseek-chat",  # 模型名称
            messages=messages,
            stream=False
        )
        
        # 返回生成的文本
        return response.choices[0].message.content
    except Exception as e:
        print(f"生成AI回复时出错: {e}")
        return "抱歉，我现在无法回答。请稍后再试。"
