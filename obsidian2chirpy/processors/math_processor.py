"""
数学公式处理模块
处理Markdown文件中的数学公式
"""

import re


def process_md(text):
    """
    处理Markdown文件中的数学公式
    将$和$$符号转换为LaTeX样式的分隔符
    
    Args:
        text: 要处理的文本
    
    Returns:
        处理后的文本
    """
    # 处理连续的"$$"块，替换为\\[和\\]
    def replace_double(match):
        replace_double.counter += 1
        return '\\\\[' if replace_double.counter % 2 == 1 else '\\\\]'
    replace_double.counter = 0  # 初始化计数器
    text = re.sub(r'\$\$', replace_double, text)  # 全局替换连续的$$

    # 处理单独的"$"块，替换为\\(和\\)
    def replace_single(match):
        replace_single.counter += 1
        return '\\\\(' if replace_single.counter % 2 == 1 else '\\\\)'
    replace_single.counter = 0  # 初始化计数器
    text = re.sub(r'\$', replace_single, text)  # 全局替换单独的$

    return text


def add_newlines(text):
    """
    在\\[前面和\\]后面添加换行
    """
    # 在\\[前面添加换行
    text = re.sub(r'(?<!\\)(\\\\)\[', r'\n\1[', text)
    
    # 在\\]后面添加换行
    text = re.sub(r'(?<!\\)(\\\\)\]', r'\1]\n', text)
    
    return text


def ensure_blank_lines_around_math_blocks(text):
    """
    确保\\[前面和\\]后面有完整的空行
    """
    # 确保\\[前面有一整个空行
    text = re.sub(r'(?<!\n\n)(\\\\)\[', r'\n\n\1[', text)
    
    # 确保\\]后面有一整个空行
    text = re.sub(r'(\\\\)\](?!\n\n)', r'\1]\n\n', text)
    
    # 避免出现过多的空行
    text = re.sub(r'\n{3,}', r'\n\n', text)
    
    return text


def replace_with_dollars(text):
    """
    将所有"\\["、"\\]"、"\\("、"\\)"都替换成"$$"
    """
    text = re.sub(r'\\\\[\[\]]', r'$$', text)  # 替换\\[和\\]
    text = re.sub(r'\\\\[\(\)]', r'$$', text)  # 替换\\(和\\)
    return text


def fix_double_braces_and_vertical_bars(text):
    """
    在数学公式中:
    1. 处理连续的花括号，在两个左花括号之间添加空格
    2. 将成对的绝对值符号 |...| 替换为 \lvert ... \rvert
    """
    # 提取所有数学区块 (处于\\[ 和 \\] 或 \\( 和 \\) 之间的内容)
    def process_math_block(match):
        math_content = match.group(1)
        
        # 处理连续的左花括号，在两个左花括号之间添加空格
        math_content = re.sub(r'{{', r'{ {', math_content)
        
        # 处理绝对值符号
        # 先处理 \left| 和 \right|
        math_content = re.sub(r'\\left\|', r'\\lvert ', math_content)
        math_content = re.sub(r'\\right\|', r'\\rvert ', math_content)
        
        # 然后处理成对的单独 | 符号
        # 计数器跟踪当前是第几个 | 符号
        def replace_vertical_bar(match):
            replace_vertical_bar.counter += 1
            if replace_vertical_bar.counter % 2 == 1:  # 奇数位的 |，替换为 \vert
                return r"\vert "  # 修复：使用单斜杠而不是双斜杠
            else:  # 偶数位的 |，替换为 \vert
                return r"\vert "  # 修复：使用单斜杠而不是双斜杠
        
        replace_vertical_bar.counter = 0  # 初始化计数器
        
        # 使用正则替换所有未被转义的单独 | 符号
        # 但要避免匹配已经处理过的 \left\lvert 和 \right\rvert
        math_content = re.sub(r'(?<!\\)(?<!\\left)(?<!\\right)\|', replace_vertical_bar, math_content)
        
        return match.group(0).replace(match.group(1), math_content)
    
    # 处理行间公式
    text = re.sub(r'\\\\[\[](.+?)\\\\[\]]', process_math_block, text, flags=re.DOTALL)
    
    # 处理行内公式
    text = re.sub(r'\\\\[\(](.+?)\\\\[\)]', process_math_block, text, flags=re.DOTALL)
    
    return text