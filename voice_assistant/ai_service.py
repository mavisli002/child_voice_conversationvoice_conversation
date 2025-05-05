"""AI service module for voice assistant."""
import os
from openai import OpenAI


def generate_response(messages):
    """
    Generate a response from the AI model.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        str: The generated response text
    """
    try:
        # Initialize OpenAI client with API key and base URL from environment variables
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), 
            base_url=os.getenv("BASE_URL")
        )
        
        # Create a chat completion
        response = client.chat.completions.create(
            model="deepseek-chat",  # Model name
            messages=messages,
            stream=False
        )
        
        # Return the generated text
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "抱歉，我现在无法回答。请稍后再试。"
