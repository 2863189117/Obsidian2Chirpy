"""
配置信息模块
包含路径和处理设置
"""

import os

# 路径设置
OUTPUT_FOLDER = "/Users/pleiades/Desktop/site/2863189117.github.io/_posts/Uncategorized"
POSTS_ROOT = "/Users/pleiades/Desktop/site/2863189117.github.io/_posts"
SOURCE_FOLDER = "/Users/pleiades/Library/Mobile Documents/iCloud~md~obsidian/Documents/Pleiades_02"
INVENTORY_PATH = os.path.join(os.path.dirname(POSTS_ROOT), "md_files_inventory.txt")
HASH_FILE_PATH = os.path.join(os.path.dirname(POSTS_ROOT), "file_hash_record.txt")
DECISIONS_FILE_PATH = 'callout_decisions.json'

# Callout类型映射
CALLOUT_TYPE_MAPPING = {
    'info': 'info',
    'tip': 'tip',
    'warning': 'warning', 
    'danger': 'danger',
    'quote': 'quote',
    'question': 'tip',  # question映射到tip
    'caution': 'warning',  # caution映射到warning
}

# 默认标题
DEFAULT_TITLE = "Untitled"