"""
Callout处理模块
处理Obsidian的callout格式，转换为Chirpy主题支持的格式
"""

import re
from ..utils import file_utils
from ..config import settings


def convert_callouts(text, file_path=None, decisions_file_path=settings.DECISIONS_FILE_PATH):
    """
    转换Markdown中的callout格式
    
    从: >[xxx] TITLE
        >say something...
    
    到: >TITLE
        >
        >say something...
        {: .prompt-info}
    
    根据类型映射规则转换callout类型，或根据用户输入决定处理方式
    
    Args:
        text: 要处理的文本内容
        file_path: 当前处理的文件路径（用于记录特定文件的决策）
        decisions_file_path: 决策文件路径
    
    Returns:
        处理后的文本
    """
    # 加载持久化的用户决策
    global_decisions = file_utils.load_user_decisions(decisions_file_path)
    
    # 用于存储本次运行中的用户决策（避免重复询问）
    session_decisions = {}
    
    # 用于识别callout区块的正则表达式，注意>和[之间可能有空格，[和!之间可能有空格
    pattern = r'(>\s*\[\s*!?\s*([^\]]+)\](.*?)(?=\n\s*>|\n\s*$)(?:\n(?:>[^\n]*\n)+))'
    
    def replace_callout(match):
        full_callout = match.group(1)
        callout_type = match.group(2).lower().strip() if match.group(2) else 'quote'
        callout_type = callout_type.split('|')[0].strip()
        title = match.group(3) if match.group(3) else ''
        
        # 处理callout内容
        lines = full_callout.split('\n')
        # 移除每行开头的 > 符号，这样后面重新构建时不会重复
        rest_lines = [line.lstrip('>').lstrip() for line in lines[1:] if line.strip()]
        
        # 构建新的callout内容时，重新添加 > 符号
        if callout_type in settings.CALLOUT_TYPE_MAPPING:
            mapped_type = settings.CALLOUT_TYPE_MAPPING[callout_type]
            title_text = title.strip() if title else ""
            # 只有当标题实际存在时才添加到第一行
            first_line = f">{title_text}" if title_text else ""
            new_callout = f"{first_line}\n"
            
            # 只有当标题实际存在时才添加空行
            if title_text:
                new_callout += ">\n"
            
            # 为每行添加 > 前缀
            new_callout += "\n".join(f">{line}" for line in rest_lines)
            
            if not new_callout.endswith('\n'):
                new_callout += '\n'
            new_callout += f"{{: .prompt-{mapped_type}}}\n"
            return new_callout
        
        # 对于未知类型，检查是否有文件特定的决策
        file_specific_key = f"{file_path}:{callout_type}" if file_path else ""
        if file_specific_key and file_specific_key in global_decisions:
            decision = global_decisions[file_specific_key]
        # 检查是否在本次会话中已做决策
        elif callout_type in session_decisions:
            decision = session_decisions[callout_type]
        else:
            # 询问用户如何处理此类型的callout
            print(f"\n发现未支持的callout类型: [{callout_type}]")
            print(f"示例内容: {title}")
            print("请选择处理方式:")
            print("I - 转换为info类型 (默认)")
            print("Q - 转换为quote类型")
            print("N - 删除此callout")
            
            valid_decisions = ['I', 'Q', 'N', '']
            while True:
                decision = input("您的选择 (I/Q/N 或回车默认为I): ").strip().upper()
                if decision in valid_decisions:
                    break
                print("无效的选择，请重新输入")
            
            # 空输入默认为I
            if decision == '':
                decision = 'I'
            
            # 存储到文件特定决策中
            if file_path:
                global_decisions[file_specific_key] = decision
            
            # 同时存储到会话决策中
            session_decisions[callout_type] = decision
            
            # 保存决策到文件
            file_utils.save_user_decisions(global_decisions, decisions_file_path)
        
        # 根据用户决策处理callout
        if decision == 'N':
            # 删除此callout
            return ""
        elif decision == 'I':
            # 转换为info类型
            # 检查标题是否只有空格
            title_text = title.strip() if title else ""
            first_line = f">{title_text}" if title_text else ""
            new_callout = f"{first_line}\n"
            
            # 如果有实际标题（不只是空格），添加一个空的引用行作为分隔
            if title_text:
                new_callout += ">\n"
            
            new_callout += '\n'.join(f">{line}" for line in rest_lines)
            if not new_callout.endswith('\n'):
                new_callout += '\n'
            new_callout += "{: .prompt-info}\n"
            return new_callout
        else:  # decision == 'Q'
            # 转换为quote类型
            # 检查标题是否只有空格
            title_text = title.strip() if title else ""
            first_line = f">{title_text}" if title_text else ">"
            new_callout = f"{first_line}\n"
            
            # 如果有实际标题（不只是空格），添加一个空的引用行作为分隔
            if title_text:
                new_callout += ">\n"
            
            new_callout += "\n".join(f">{line}" for line in rest_lines)
            if not new_callout.endswith('\n'):
                new_callout += '\n'
            new_callout += "{: .prompt-quote}\n"
            return new_callout
    
    # 替换所有匹配的callout
    return re.sub(pattern, replace_callout, text, flags=re.DOTALL)


def ensure_blank_lines_before_callouts(text):
    """
    确保所有callout（格式为 >[!xxx]）前面有空行
    """
    # 匹配任何callout的开始行（以>开头，包含[!xxx]）
    pattern = r'(?<!\n\n)(>\s*\[\s*!?\s*[^\]]+\])'
    
    # 在callout前添加空行
    text = re.sub(pattern, r'\n\1', text)
    
    return text


def separate_adjacent_callouts(text):
    """
    在相邻的callout之间添加空行分隔
    查找两个callout之间的分界点（第二个callout的开始处）并在此处插入空行
    """
    # 匹配两个callout的分界处，即前一行以>开头，当前行也以>开头且包含[!xxx]标记
    pattern = r'(>\s*[^\n]*\n)(>\s*\[\s*!?\s*[^\]]+\])'
    
    # 在这种分界处添加一个空行
    text = re.sub(pattern, r'\1\n\2', text)
    
    return text