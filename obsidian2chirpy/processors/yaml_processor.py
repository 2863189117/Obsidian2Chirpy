"""
YAML前置元数据处理模块
处理Markdown文件的YAML前置信息
"""

import re
import os
from ..config import settings


def process_yaml_frontmatter(text, title=settings.DEFAULT_TITLE):
    """
    处理YAML前置元数据:
    1. 提取标题 (使用文件名)
    2. 将'created'改为'date'
    3. 将'updated'改为'last_modified_at'
    4. 添加空的categories、math和tags字段
    5. 删除其他键值对
    6. 确保日期时间的秒数小于60
    7. 移除时间后的时区信息
    
    Args:
        text: 要处理的文本
        title: 文件标题，默认为"Untitled"
        
    Returns:
        处理后的文本
    """
    # 检查文档是否有YAML前置元数据
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    
    if not yaml_match:
        # 如果没有元数据块，创建新的元数据块
        yaml_content = f"---\ntitle: \"{title}\"\ndate: \ncategories: \nmath: true\ntags: \n---\n\n"
        return yaml_content + text
    
    # 提取元数据内容
    yaml_content = yaml_match.group(1)
    rest_of_doc = text[yaml_match.end():]
    
    # 提取已存在的值
    created_match = re.search(r'created:\s*(.*?)(?:\n|$)', yaml_content)
    created = created_match.group(1).strip() if created_match else ""
    
    # 去掉时间中的时区信息（如 +0800）
    if created and len(created) > 19:  # 标准格式 "YYYY-MM-DD HH:MM:SS" 是19个字符
        timezone = created[20:]  # 保存时区信息以便后面使用
        created = created[:19]  # 只保留前19个字符
    else:
        timezone = ""  # 确保timezone变量存在
    
    # 确保created日期时间的秒数小于60
    if created and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', created):
        date_parts = created.split(' ')
        if len(date_parts) == 2:
            time_parts = date_parts[1].split(':')
            if len(time_parts) == 3 and int(time_parts[2]) >= 60:
                time_parts[2] = str(min(int(time_parts[2]), 59)).zfill(2)
                date_parts[1] = ':'.join(time_parts)
                created = ' '.join(date_parts)
    
    updated_match = re.search(r'updated:\s*(.*?)(?:\n|$)', yaml_content)
    updated = updated_match.group(1).strip() if updated_match else ""
    
    # 去掉时间中的时区信息（如 +0800）
    if updated and len(updated) > 19:  # 标准格式 "YYYY-MM-DD HH:MM:SS" 是19个字符
        timezone = updated[20:]
        updated = updated[:19]  # 只保留前19个字符
    
    # 确保updated日期时间的秒数小于60
    if updated and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', updated):
        date_parts = updated.split(' ')
        if len(date_parts) == 2:
            time_parts = date_parts[1].split(':')
            if len(time_parts) == 3 and int(time_parts[2]) >= 60:
                time_parts[2] = str(min(int(time_parts[2]), 59)).zfill(2)
                date_parts[1] = ':'.join(time_parts)
                updated = ' '.join(date_parts)
    
    # 创建新的YAML前置元数据
    new_yaml = f"---\ntitle: \"{title}\"\n"
    if created:
        new_yaml += f"date: {created}"
        if timezone:
            new_yaml += f" {timezone}"
        new_yaml += "\n"
    if updated:
        new_yaml += f"last_modified_at: {updated}"
        if timezone:
            new_yaml += f" {timezone}"
        new_yaml += "\n"
    
    new_yaml += "categories: \nmath: true\ntags: \n---\n\n"
    
    return new_yaml + rest_of_doc