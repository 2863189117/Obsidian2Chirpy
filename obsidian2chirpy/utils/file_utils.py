"""
文件处理工具函数
提供文件读写、搜索等操作
"""

import os
import hashlib
import json
import re

from ..config import settings
from ..utils import text_utils


def calculate_file_hash(file_path):
    """
    计算文件的MD5哈希值
    
    Args:
        file_path: 文件路径
    
    Returns:
        MD5哈希值字符串
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_file_hashes(hash_file_path):
    """
    从记录文件中读取文件路径和对应的哈希值
    
    Args:
        hash_file_path: 哈希记录文件路径
    
    Returns:
        字典 {文件路径: 哈希值}
    """
    file_hashes = {}
    
    try:
        # 确保文件所在目录存在
        hash_file_dir = os.path.dirname(hash_file_path)
        if not os.path.exists(hash_file_dir):
            os.makedirs(hash_file_dir)
            
        if os.path.exists(hash_file_path):
            with open(hash_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line and not line.startswith('#'):
                        parts = line.strip().split(':', 1)
                        file_path = parts[0].strip()
                        hash_value = parts[1].strip()
                        file_hashes[file_path] = hash_value
        else:
            # 文件不存在，创建空文件
            with open(hash_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# 文件哈希值记录 - 创建时间: {text_utils.format_time_with_limited_seconds()}\n\n")
            print(f"哈希记录文件不存在，已创建新文件: {hash_file_path}")
    except Exception as e:
        print(f"读取哈希记录失败: {e}")
    return file_hashes


def save_file_hashes(hash_file_path, file_hashes):
    """
    将文件路径和对应的哈希值保存到记录文件中
    
    Args:
        hash_file_path: 哈希记录文件路径
        file_hashes: 字典 {文件路径: 哈希值}
    """
    try:
        with open(hash_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 文件哈希值记录 - 更新时间: {text_utils.format_time_with_limited_seconds()}\n\n")
            for file_path, hash_value in sorted(file_hashes.items()):
                f.write(f"{file_path}: {hash_value}\n")
    except Exception as e:
        print(f"保存哈希记录失败: {e}")


def search_files_by_name(search_name, source_folder):
    """
    在源文件夹中搜索匹配给定文件名的文件
    
    Args:
        search_name: 要搜索的文件名（不包含路径）
        source_folder: 源文件夹路径
    
    Returns:
        匹配文件路径的列表
    """
    matching_files = []
    
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                # 不区分大小写进行匹配
                if search_name.lower() in file.lower():
                    matching_files.append(os.path.join(root, file))
    
    return matching_files


def search_folders_by_name(search_name, source_folder):
    """
    在源文件夹中搜索匹配给定名称的文件夹
    
    Args:
        search_name: 要搜索的文件夹名称
        source_folder: 源文件夹路径
    
    Returns:
        匹配文件夹路径的列表
    """
    matching_folders = []
    
    for root, dirs, _ in os.walk(source_folder):
        for dir_name in dirs:
            # 不区分大小写进行匹配
            if search_name.lower() in dir_name.lower():
                matching_folders.append(os.path.join(root, dir_name))
    
    return matching_folders


def scan_posts_directory(root_path, output_file='md_files_inventory.txt'):
    """
    递归搜索目录及其子目录下所有的md文件，记录其标题和路径到一个txt文件中
    
    Args:
        root_path: _posts目录的根路径
        output_file: 输出的记录文件名
    
    Returns:
        包含所有文件信息的字典：{原始标题: 完整路径}
    """
    inventory = {}
    output_path = os.path.join(os.path.dirname(root_path), output_file)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 遍历目录
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                # 提取原始标题（移除日期前缀）
                original_title = text_utils.extract_original_title(file)
                if original_title:
                    inventory[original_title] = file_path
    
    # 将信息写入txt文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 文档索引 - 更新时间: {text_utils.format_time_with_limited_seconds()}\n\n")
        for title, path in inventory.items():
            f.write(f"* {title}: {path}\n")
    
    return inventory


def find_source_files_from_inventory(inventory_path, source_folder):
    """
    根据索引文件找到源文件夹中对应的源文件
    使用正则表达式从文章路径中提取标题
    
    Args:
        inventory_path: 文章索引文件路径
        source_folder: 源文件文件夹路径
    
    Returns:
        字典 {源文件路径: 对应的文章路径}
    """
    # 从索引文件中读取文章路径
    post_paths = {}
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('* '):  # 匹配"* 标题: 路径"格式的行
                    parts = line[2:].split(':', 1)
                    if len(parts) == 2:
                        path = parts[1].strip()
                        # 使用正则表达式从路径中提取标题（去除日期前缀）
                        title_match = re.search(r'/(\d{4}-\d{2}-\d{2}-(.*?))(\.md|\.markdown)?$', path)
                        if title_match:
                            title = title_match.group(2).lower()  # 提取不含日期前缀的标题
                            post_paths[title] = path
    
    # 在源文件夹中查找对应的源文件
    source_files = {}
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                file_name_no_ext = os.path.splitext(file)[0].lower()
                
                # 检查是否匹配任何文章标题
                if file_name_no_ext in post_paths:
                    source_files[file_path] = post_paths[file_name_no_ext]
    
    return source_files


def load_user_decisions(decisions_file_path=settings.DECISIONS_FILE_PATH):
    """
    从JSON文件中加载用户对callout类型的处理决策
    
    Args:
        decisions_file_path: 决策文件路径
        
    Returns:
        包含用户决策的字典: {callout_type: decision}
    """
    user_decisions = {}
    
    # 确保文件所在目录存在
    decisions_dir = os.path.dirname(decisions_file_path)
    if decisions_dir and not os.path.exists(decisions_dir):
        os.makedirs(decisions_dir)
    
    try:
        if os.path.exists(decisions_file_path):
            with open(decisions_file_path, 'r', encoding='utf-8') as f:
                user_decisions = json.load(f)
            print(f"已加载 {len(user_decisions)} 个callout类型的处理决策")
        else:
            # 文件不存在，创建空文件
            with open(decisions_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"未找到决策记录文件，已创建新文件: {decisions_file_path}")
    except Exception as e:
        print(f"加载用户决策失败: {e}")
    
    return user_decisions


def save_user_decisions(user_decisions, decisions_file_path=settings.DECISIONS_FILE_PATH):
    """
    将用户对callout类型的处理决策保存到JSON文件
    
    Args:
        user_decisions: 包含用户决策的字典
        decisions_file_path: 决策文件路径
    """
    try:
        # 确保文件所在目录存在
        decisions_dir = os.path.dirname(decisions_file_path)
        if decisions_dir and not os.path.exists(decisions_dir):
            os.makedirs(decisions_dir)
            
        with open(decisions_file_path, 'w', encoding='utf-8') as f:
            json.dump(user_decisions, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(user_decisions)} 个callout类型的处理决策")
    except Exception as e:
        print(f"保存用户决策失败: {e}")