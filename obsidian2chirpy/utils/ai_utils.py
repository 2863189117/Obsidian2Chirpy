"""
AI工具模块
提供AI相关功能，如生成摘要等
"""

import requests
import json
import os
from ..config import settings

def generate_summary(content, max_length=150):
    """
    使用AI生成文章摘要
    
    Args:
        content: 要生成摘要的文章内容
        max_length: 摘要最大长度(字符数)
    
    Returns:
        生成的摘要字符串，如果生成失败则返回None
    """
    # 检查API密钥是否存在
    if not settings.AI_API_KEY:
        print("⚠️ 未设置AI API密钥，无法生成摘要")
        return None
    
    try:
        # 准备请求数据
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.AI_API_KEY}"
        }
        
        # 构建请求体，根据您使用的AI服务调整格式
        data = {
            "model": settings.AI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的文章摘要生成器。你的任务是将给定的文章内容转换为简短的摘要，摘要应该清晰简洁地概括文章的主要内容。"},
                {"role": "user", "content": f"请为以下文章内容生成一个大约{max_length}字符的简短摘要，不要使用'这篇文章'、'本文'等指代词开头，非汉字或英文字符不计入字符数：\n\n{content[:4000]}"}
            ],
            "max_tokens": 100,
            "temperature": 0.5
        }
        
        # 发送API请求
        response = requests.post(settings.AI_API_URL, headers=headers, json=data)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            # 根据API的返回格式提取摘要内容
            summary = result["choices"][0]["message"]["content"].strip()
            summary += "\n <---此摘要由AI生成，可能完全不准确。--->"
            # 确保摘要不超过最大长度
            if len(summary) > max_length+50:
                summary = summary[:max_length-3] + "..."
            
            return summary
        else:
            print(f"⚠️ 摘要生成失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"⚠️ 摘要生成过程中出错: {str(e)}")
        return None
