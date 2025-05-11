"""
Markdown处理模块
综合各种处理器对Markdown内容进行处理
"""

import os
from ..processors import yaml_processor, math_processor, callout_processor
from ..utils import text_utils
from ..config import settings


def process_and_format_md(text, file_path=None):
    """
    处理Markdown文件中的数学公式、callout等内容并格式化
    
    Args:
        text: 要处理的文本内容
        file_path: 文件路径，用于提取文件名作为标题
    
    Returns:
        处理后的文本
    """
    # 从文件路径中提取文件名作为标题
    title = settings.DEFAULT_TITLE
    if file_path:
        # 提取文件名（不含扩展名）
        title = os.path.splitext(os.path.basename(file_path))[0]
    
    # 先处理YAML前置元数据
    text = yaml_processor.process_yaml_frontmatter(text, title)
    
    # 将占位符标题替换为实际文件名
    text = text.replace(f'title: "{settings.DEFAULT_TITLE}"', f'title: "{title}"', 1)
    
    # 确保相邻callout之间有空行分隔
    text = callout_processor.separate_adjacent_callouts(text)
    
    # 转换Wiki链接格式
    text = text_utils.convert_wiki_links(text)
    
    # 转换callout格式（传递文件路径用于记录特定文件的决策）
    text = callout_processor.convert_callouts(text, file_path)
    
    # 处理数学公式
    text = math_processor.process_md(text)
    
    # 处理数学公式中的连续花括号和绝对值符号
    text = math_processor.fix_double_braces_and_vertical_bars(text)
    
    # 添加换行
    text = math_processor.add_newlines(text)
    
    # 确保数学块周围有完整的空行
    text = math_processor.ensure_blank_lines_around_math_blocks(text)
    
    # 最后将所有LaTeX分隔符替换为$$
    text = math_processor.replace_with_dollars(text)
    
    return text