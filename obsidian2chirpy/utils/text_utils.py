"""
文本处理工具函数
提供格式化、解析等文本处理操作
"""

import re
import time


def format_time_with_limited_seconds(format_str="%Y-%m-%d %H:%M:%S"):
    """
    格式化当前时间，确保秒数不超过60
    
    Args:
        format_str: 时间格式字符串
        
    Returns:
        格式化的时间字符串，秒数限制在0-59范围内
    """
    # 获取当前时间
    current_time = time.localtime()
    # 创建一个新的时间元组，将秒数限制在0-59范围内
    limited_time = time.struct_time((
        current_time.tm_year,
        current_time.tm_mon,
        current_time.tm_mday,
        current_time.tm_hour,
        current_time.tm_min,
        min(current_time.tm_sec, 59),  # 确保秒数不超过59
        current_time.tm_wday,
        current_time.tm_yday,
        current_time.tm_isdst
    ))
    # 使用修改后的时间元组进行格式化
    return time.strftime(format_str, limited_time)


def extract_date_from_content(text):
    """
    从文档内容中提取日期信息
    返回格式为YYYY-MM-DD的日期字符串，如果未找到则返回None
    """
    # 查找YAML前置元数据中的日期
    date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', text)
    if date_match:
        return date_match.group(1)
    return None


def extract_original_title(filename):
    """
    从文件名中提取原始标题部分（去掉日期前缀YYYY-MM-DD-）
    
    Args:
        filename: 文件名
    
    Returns:
        原始标题部分，如果没有日期前缀则返回None
    """
    # 匹配YYYY-MM-DD-格式的日期前缀
    match = re.match(r'\d{4}-\d{2}-\d{2}-(.*)', filename)
    if match:
        return match.group(1)
    return None


def extract_yaml_and_content(text):
    """
    从Markdown文本中提取所有YAML前置元数据块和内容部分
    可能有多个YAML块，格式如：
    ---
    AAA
    ---
    BBB
    ---
    
    Args:
        text: 完整的Markdown文本
    
    Returns:
        元组 (yaml_part, content_part)
    """
    # 找到所有连续的YAML块
    # 首先检查文本是否以 --- 开头
    if not text.strip().startswith('---'):
        # 如果没有YAML前置元数据，则整个文本都是内容部分
        return "", text
    
    # 查找所有的 --- 分隔行
    yaml_separator_positions = []
    lines = text.splitlines(True)  # 保留换行符
    line_position = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            yaml_separator_positions.append(line_position)
        line_position += len(line)
    
    # 如果没有足够的分隔符，或者不是以 --- 开头，则视为无YAML
    if len(yaml_separator_positions) < 2:
        return "", text
    
    # 查找第一个二级标题位置（以 ## 开头的行）
    first_header_position = -1
    line_position = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('## '):
            first_header_position = line_position
            break
        line_position += len(line)
    
    # 确定YAML块结束位置
    # 找到最后一个YAML分隔符，如果它在第一个二级标题之前
    last_yaml_separator = -1
    for pos in yaml_separator_positions:
        if first_header_position == -1 or pos < first_header_position:
            last_yaml_separator = pos
    
    # 如果找不到有效的YAML块结束位置，返回原文本
    if last_yaml_separator == -1:
        return "", text
    
    # 确定最后一个YAML分隔符的结束位置（包括换行符）
    yaml_end_position = last_yaml_separator + 3  # --- 的长度为3
    if yaml_end_position < len(text) and text[yaml_end_position] == '\n':
        yaml_end_position += 1
    
    # 提取所有YAML块作为一个整体
    yaml_part = text[:yaml_end_position]
    
    # 内容部分是剩余的文本
    content_part = text[yaml_end_position:]
    
    return yaml_part, content_part


def convert_wiki_links(text):
    """
    将Obsidian的Wiki链接格式转换:
    [[xxx|yyy]] 转换为 *yyy*
    [[xxx]] 转换为 *xxx*
    [[xxx#yyy]] 转换为 *xxx#yyy*
    """
    # 先匹配[[xxx|yyy]]格式 - 带别名的链接
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'*\2*', text)
    
    # 再匹配单独的[[xxx]]格式，包括可能带有#的内部链接
    text = re.sub(r'\[\[(.*?)\]\]', r'*\1*', text)
    
    return text