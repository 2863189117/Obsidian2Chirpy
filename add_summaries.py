#!/usr/bin/env python
"""
临时程序：为现有的Chirpy博客文章添加AI摘要

此脚本将读取指定_posts目录中的所有Markdown文件，
为每个文件生成AI摘要，并将其添加到文件的YAML前置元数据中的description字段。

用法:
    python add_summaries.py [选项]

选项:
    --all          处理所有文件，包括已有摘要的文件
    --limit N      限制处理文件数量为N（默认处理所有）
    --category CAT 只处理特定分类的文件
    --help, -h     显示帮助信息
"""

import os
import re
import sys
import time
import argparse
import re
import os
import sys
import time
import argparse
from obsidian2chirpy.config import settings
from obsidian2chirpy.utils import ai_utils

def add_summary_to_file(file_path, override_existing=False):
    """
    为单个文件添加AI摘要
    
    Args:
        file_path: 文件路径
        override_existing: 是否覆盖已有的摘要
        
    Returns:
        bool: 是否成功添加摘要
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件是否已有description字段
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            print(f"⚠️ 文件 {os.path.basename(file_path)} 没有YAML前置元数据，跳过")
            return False
        
        yaml_content = yaml_match.group(1)
        if re.search(r'description:', yaml_content) and not override_existing:
            print(f"⚠️ 文件 {os.path.basename(file_path)} 已有摘要，跳过")
            return False
        
        # 提取正文内容用于生成摘要
        rest_of_doc = content[yaml_match.end():]
        
        # 从正文内容中删除Markdown特殊格式
        content_for_summary = re.sub(r'```.*?```', '', rest_of_doc, flags=re.DOTALL)
        content_for_summary = re.sub(r'<.*?>', '', content_for_summary)
        content_for_summary = re.sub(r'!\[.*?\]\(.*?\)', '', content_for_summary)
        content_for_summary = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content_for_summary)
        
        # 生成摘要
        print(f"正在为文件 {os.path.basename(file_path)} 生成摘要...")
        summary = ai_utils.generate_summary(content_for_summary, settings.SUMMARY_MAX_LENGTH)
        
        if not summary:
            print(f"❌ 文件 {os.path.basename(file_path)} 摘要生成失败")
            return False
        
        # 处理摘要中可能包含的引号，确保YAML格式正确
        summary = summary.replace('"', '\\"')
        
        # 将摘要添加到YAML前置元数据中
        new_yaml = yaml_content.rstrip() + f'\ndescription: "{summary}"\n'
        new_content = re.sub(r'^---\s*\n(.*?)\n---\s*\n', f'---\n{new_yaml}\n---\n\n', content, flags=re.DOTALL)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 输出简化的摘要信息
        truncated_summary = summary[:50] + "..." if len(summary) > 50 else summary
        print(f"✅ 文件 {os.path.basename(file_path)} 摘要添加成功")
        print(f"   摘要: {truncated_summary}")
        return True
    
    except Exception as e:
        print(f"❌ 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return False

def process_all_posts(override_existing=False, limit=None, category=None):
    """
    处理_posts目录中的所有Markdown文件
    
    Args:
        override_existing: 是否覆盖已有摘要
        limit: 限制处理的文件数量
        category: 只处理特定分类的文件
    """
    if not os.path.exists(settings.POSTS_ROOT):
        print(f"❌ 目录不存在: {settings.POSTS_ROOT}")
        return
    
    # 检查API密钥
    if not settings.AI_API_KEY:
        api_key = input("请输入AI API密钥: ").strip()
        if api_key:
            settings.AI_API_KEY = api_key
        else:
            print("❌ 未提供API密钥，无法生成摘要")
            return
    
    print(f"开始处理 {settings.POSTS_ROOT} 中的Markdown文件...")
    if override_existing:
        print("已启用覆盖现有摘要选项")
    if limit:
        print(f"将只处理 {limit} 个文件")
    if category:
        print(f"将只处理 {category} 分类的文件")
    
    # 统计信息
    total_files = 0
    processed_files = 0
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    # 遍历目录
    for root, _, files in os.walk(settings.POSTS_ROOT):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                
                # 如果指定了分类，检查是否匹配
                if category:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    category_match = re.search(r'categories:\s*\[(.*?)\]', content)
                    if not category_match or category.lower() not in category_match.group(1).lower():
                        continue
                
                total_files += 1
                
                # 如果设置了限制，并且已经达到限制，停止处理
                if limit and processed_files >= limit:
                    break
                
                processed_files += 1
                try:
                    result = add_summary_to_file(file_path, override_existing)
                    if result:
                        success_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    print(f"❌ 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
                    failed_count += 1
                
                # 添加延迟，避免API调用过于频繁
                time.sleep(1)
    
    print("\n处理完成！统计信息：")
    print(f"- 总文件数：{total_files}")
    print(f"- 成功添加摘要数：{success_count}")
    print(f"- 跳过文件数（已有摘要）：{skipped_count}")
    print(f"- 处理失败数：{failed_count}")

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='为现有的Chirpy博客文章添加AI摘要')
    parser.add_argument('--all', action='store_true', help='处理所有文件，包括已有摘要的文件')
    parser.add_argument('--limit', type=int, help='限制处理文件数量')
    parser.add_argument('--category', help='只处理特定分类的文件')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据命令行参数设置处理选项
    override_existing = args.all
    limit = args.limit
    category = args.category
    
    process_all_posts(override_existing=override_existing, limit=limit, category=category)
