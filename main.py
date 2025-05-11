#!/usr/bin/env python
"""
Obsidian2Chirpy 主程序
将Obsidian格式的Markdown文件转换为Chirpy主题博客兼容的格式

用法：
python main.py [文件名/文件夹名/路径]
"""

import sys
import os
import re
import time
import hashlib
import json

# 导入重构后的模块
from obsidian2chirpy.core.file_processor import process_folder


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
    else:
        # 获取用户输入的文件名、文件夹名或路径
        input_text = input("请输入要处理的Markdown文件名、文件夹名或路径（留空则自动处理源文件夹）：").strip()
    
    # 处理给定输入或自动处理
    # 先尝试去除输入可能带的引号
    cleaned_input = input_text.strip('\'"')
    process_folder(cleaned_input)
