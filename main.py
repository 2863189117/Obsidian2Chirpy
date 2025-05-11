#!/usr/bin/env python
"""
Obsidian2Chirpy 主程序
将Obsidian格式的Markdown文件转换为Chirpy主题博客兼容的格式

用法：
python main.py [选项] [文件名/文件夹名/路径]

选项:
--summary, -s     启用AI自动生成文章摘要
--help, -h        显示帮助信息
"""

import sys
import os
import re
import time
import hashlib
import json
import argparse

# 导入重构后的模块
from obsidian2chirpy.core.file_processor import process_folder
from obsidian2chirpy.config import settings


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将Obsidian格式的Markdown文件转换为Chirpy主题博客兼容的格式')
    parser.add_argument('--summary', '-s', action='store_true', help='启用AI自动生成文章摘要')
    parser.add_argument('input_path', nargs='?', default='', help='要处理的文件名、文件夹名或路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据命令行参数设置是否启用摘要生成
    if args.summary:
        settings.ENABLE_AUTO_SUMMARY = True
        print("已启用AI自动生成文章摘要功能")
        if not settings.AI_API_KEY:
            api_key = input("请输入AI API密钥（按Enter跳过）: ").strip()
            if api_key:
                settings.AI_API_KEY = api_key
            else:
                print("⚠️ 未提供API密钥，摘要功能将被禁用")
                settings.ENABLE_AUTO_SUMMARY = False
    else:
        settings.ENABLE_AUTO_SUMMARY = False
    
    # 处理输入路径
    input_path = args.input_path
    if not input_path:
        # 获取用户输入的文件名、文件夹名或路径
        input_path = input("请输入要处理的Markdown文件名、文件夹名或路径（留空则自动处理源文件夹）：").strip()
    
    # 先尝试去除输入可能带的引号
    cleaned_input = input_path.strip('\'"')
    
    # 处理给定输入或自动处理
    process_folder(cleaned_input)
