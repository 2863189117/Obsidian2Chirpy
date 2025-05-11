"""
文件处理核心模块
处理单个文件或多个文件
"""

import os
import re
from ..processors import markdown_processor
from ..utils import file_utils, text_utils
from ..config import settings


def process_file(file_path, output_folder=settings.OUTPUT_FOLDER):
    """
    处理单个Markdown文件
    
    Args:
        file_path: 要处理的文件路径
        output_folder: 输出目录路径
    
    Returns:
        是否成功处理
    """
    # 移除路径两端可能存在的引号
    file_path = file_path.strip('\'"')
    
    print(f"正在处理：{file_path}")
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        # 获取原始文件名（无路径）
        original_filename = os.path.basename(file_path)
        
        # 扫描_posts目录，获取已存在文件的清单
        existing_files = file_utils.scan_posts_directory(settings.POSTS_ROOT)
        
        # 检查文件是否已存在（通过原始标题匹配）
        file_exists = False
        existing_path = None
        
        # 对比原始文件名和已存在文件的原始标题
        for title, path in existing_files.items():
            # 忽略文件扩展名和大小写进行比较
            if os.path.splitext(original_filename.lower())[0] == os.path.splitext(title.lower())[0]:
                file_exists = True
                existing_path = path
                break
        
        if file_exists and existing_path:
            print(f"文件已存在于: {existing_path}")
            
            # 读取现有文件
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # 提取现有文件的YAML前置元数据和内容
            yaml_part, _ = text_utils.extract_yaml_and_content(existing_content)
            
            # 检查是否包含 final_version: true
            if re.search(r'final_version\s*:\s*true', yaml_part, re.IGNORECASE):
                print(f"⚠️ 文件标记为最终版本，跳过更新: {existing_path}")
                return True  # 返回True表示处理成功，但实际上是跳过了更新
            
            # 从输入文本中提取YAML元数据，检查是否有updated字段
            input_yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', input_text, re.DOTALL)
            updated_value = None
            
            if input_yaml_match:
                input_yaml_content = input_yaml_match.group(1)
                # 从输入文件的YAML中提取updated字段
                updated_match = re.search(r'updated:\s*(.*?)(?:\n|$)', input_yaml_content)
                if updated_match:
                    updated_value = updated_match.group(1).strip()
            
            # 如果从输入文件中找到了updated值，则更新last_modified_at字段
            if updated_value:
                # 检查是否已有last_modified_at字段
                if "last_modified_at:" in yaml_part:
                    # 替换last_modified_at字段值
                    yaml_part = re.sub(
                        r'last_modified_at:.*?\n', 
                        f'last_modified_at: {updated_value}\n', 
                        yaml_part
                    )
                else:
                    # 如果没有last_modified_at字段，则在date字段后添加
                    yaml_part = re.sub(
                        r'(date:.*?\n)', 
                        f'\\1last_modified_at: {updated_value}\n', 
                        yaml_part
                    )
            
            # 处理输入文本内容
            processed_text = markdown_processor.process_and_format_md(input_text, file_path)
            _, new_content = text_utils.extract_yaml_and_content(processed_text)
            
            # 合并：保留更新后的YAML元数据，更新内容部分
            output_text = f"{yaml_part}\n{new_content}"
            
            # 更新现有文件
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            
            print(f"✓ 已更新现有文件：{existing_path}")
            if updated_value:
                print(f"  - 已更新last_modified_at字段为: {updated_value}")
        else:
            # 文件不存在，按原逻辑处理
            processed_text = markdown_processor.process_and_format_md(input_text, file_path)
            
            # 从处理后的内容中提取日期，用于文件名
            date_str = text_utils.extract_date_from_content(processed_text)
            
            # 决定输出文件名
            if date_str:
                # 格式化为 YYYY-MM-DD-原文件名
                output_filename = f"{date_str}-{original_filename}"
            else:
                # 如果没找到日期，保持原文件名
                output_filename = original_filename
            
            # 创建输出文件路径
            output_file_path = os.path.join(output_folder, output_filename)
            
            # 写入处理后的内容到新文件
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_text)
            
            print(f"✓ 新建文件：{output_file_path}")
        
        return True
        
    except Exception as e:
        print(f"× 处理失败：{file_path} - {str(e)}")
        return False


def process_folder(file_name_or_path):
    """
    根据文件名或文件夹名处理匹配的文件，或处理指定的路径
    当输入为空时，自动处理特定目录
    """
    processed_count = 0
    failed_count = 0
    skipped_count = 0
    updated_count = 0
    unchanged_count = 0
    
    # 确保输出文件夹存在
    if not os.path.exists(settings.OUTPUT_FOLDER):
        os.makedirs(settings.OUTPUT_FOLDER)
    
    # 始终更新文章索引文件
    print("更新文章索引文件...")
    inventory = file_utils.scan_posts_directory(settings.POSTS_ROOT, os.path.basename(settings.INVENTORY_PATH))
    print(f"索引文件已更新，共收录 {len(inventory)} 篇文章")
    
    # 加载文件哈希记录
    file_hashes = file_utils.load_file_hashes(settings.HASH_FILE_PATH)
    updated_hashes = {}  # 用于记录本次处理后的哈希值
    
    # 检查输入是否为空
    if not file_name_or_path.strip():
        print("输入为空，自动处理源文件夹中的文件...")
        
        # 从源文件夹查找对应的源文件
        source_files = file_utils.find_source_files_from_inventory(settings.INVENTORY_PATH, settings.SOURCE_FOLDER)
        
        if not source_files:
            print("没有找到匹配的源文件，请检查源文件夹和索引文件")
            return
        
        print(f"找到 {len(source_files)} 个匹配的源文件")
        
        # 处理每个源文件
        for source_path, post_path in source_files.items():
            # 计算源文件的哈希值
            try:
                current_hash = file_utils.calculate_file_hash(source_path)
                
                # 检查文件是否已经处理过且未修改
                if source_path in file_hashes and file_hashes[source_path] == current_hash:
                    print(f"跳过未修改的文件：{source_path}")
                    unchanged_count += 1
                    # 保存当前哈希值
                    updated_hashes[source_path] = current_hash
                    continue
                
                print(f"处理源文件：{source_path} -> {post_path}")
                
                # 处理文件并更新对应的文章
                with open(source_path, 'r', encoding='utf-8') as f:
                    input_text = f.read()
                
                # 读取目标文章
                with open(post_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # 提取YAML前置元数据和内容
                yaml_part, _ = text_utils.extract_yaml_and_content(existing_content)
                
                # 检查是否包含 final_version: true
                if re.search(r'final_version\s*:\s*true', yaml_part, re.IGNORECASE):
                    print(f"⚠️ 文件标记为最终版本，跳过更新: {post_path}")
                    unchanged_count += 1
                    # 仍然保存当前哈希值，避免重复提示
                    updated_hashes[source_path] = current_hash
                    continue
                
                # 从输入文本中提取YAML元数据，检查是否有updated字段
                input_yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', input_text, re.DOTALL)
                updated_value = None
                
                if input_yaml_match:
                    input_yaml_content = input_yaml_match.group(1)
                    # 从输入文件的YAML中提取updated字段
                    updated_match = re.search(r'updated:\s*(.*?)(?:\n|$)', input_yaml_content)
                    if updated_match:
                        updated_value = updated_match.group(1).strip()
                
                # 如果从输入文件中找到了updated值，则更新last_modified_at字段
                if updated_value:
                    # 检查是否已有last_modified_at字段
                    if "last_modified_at:" in yaml_part:
                        # 替换last_modified_at字段值
                        yaml_part = re.sub(
                            r'last_modified_at:.*?\n', 
                            f'last_modified_at: {updated_value}\n', 
                            yaml_part
                        )
                    else:
                        # 如果没有last_modified_at字段，则在date字段后添加
                        yaml_part = re.sub(
                            r'(date:.*?\n)', 
                            f'\\1last_modified_at: {updated_value}\n', 
                            yaml_part
                        )
                
                # 处理输入文本内容
                processed_text = markdown_processor.process_and_format_md(input_text, source_path)
                _, new_content = text_utils.extract_yaml_and_content(processed_text)
                
                # 合并：保留更新后的YAML元数据，更新内容部分
                output_text = f"{yaml_part}\n{new_content}"
                
                # 更新文章文件
                with open(post_path, 'w', encoding='utf-8') as f:
                    f.write(output_text)
                
                # 更新哈希值记录
                updated_hashes[source_path] = current_hash
                
                print(f"✓ 已更新文章：{post_path}")
                if updated_value:
                    print(f"  - 已更新last_modified_at字段为: {updated_value}")
                
                updated_count += 1
                processed_count += 1
                
            except Exception as e:
                print(f"× 处理失败：{source_path} - {str(e)}")
                failed_count += 1
        
        # 保存更新后的哈希值记录
        file_utils.save_file_hashes(settings.HASH_FILE_PATH, updated_hashes)
    
    else:
        # 先移除输入路径两端可能存在的引号
        path = file_name_or_path.strip('\'"')
        
        # 检查输入是否是完整路径
        if os.path.exists(path):
            # 是完整路径，按原来的逻辑处理
            
            # 处理单个文件
            if os.path.isfile(path):
                if path.lower().endswith(('.md', '.markdown')):
                    result = process_file(path, settings.OUTPUT_FOLDER)
                    if result:
                        processed_count += 1
                    else:
                        failed_count += 1
                else:
                    print(f"跳过非Markdown文件：{path}")
                    skipped_count += 1
            
            # 处理文件夹
            elif os.path.isdir(path):
                # 遍历文件夹中的所有文件
                for root, _, files in os.walk(path):
                    for file in files:
                        # 只处理Markdown文件
                        file_path = os.path.join(root, file)
                        if file.lower().endswith(('.md', '.markdown')):
                            result = process_file(file_path, settings.OUTPUT_FOLDER)
                            if result:
                                processed_count += 1
                            else:
                                failed_count += 1
                        else:
                            skipped_count += 1
        else:
            # 首先尝试作为文件夹名搜索
            matching_folders = file_utils.search_folders_by_name(path, settings.SOURCE_FOLDER)
            
            # 再尝试作为文件名搜索
            matching_files = file_utils.search_files_by_name(path, settings.SOURCE_FOLDER)
            
            # 如果既找到了文件夹又找到了文件，询问用户想要处理哪种类型
            if matching_folders and matching_files:
                print(f"找到匹配'{path}'的文件和文件夹:")
                print("文件夹:")
                for i, folder_path in enumerate(matching_folders, 1):
                    print(f"F{i}. {folder_path}")
                print("\n文件:")
                for i, file_path in enumerate(matching_files, 1):
                    print(f"M{i}. {file_path}")
                
                # 获取用户选择
                while True:
                    try:
                        choice = input("请选择要处理的项目类型和编号（如F1处理第1个文件夹, M2处理第2个文件，输入q退出）: ").strip()
                        if choice.lower() == 'q':
                            return
                        if not (choice.startswith('F') or choice.startswith('f') or choice.startswith('M') or choice.startswith('m')):
                            print("无效的选择，请以F或M开头")
                            continue
                        
                        item_type = choice[0].upper()
                        try:
                            choice_index = int(choice[1:]) - 1
                            if item_type == 'F' and 0 <= choice_index < len(matching_folders):
                                # 处理选择的文件夹
                                folder_path = matching_folders[choice_index]
                                print(f"处理文件夹: {folder_path}")
                                for root, _, files in os.walk(folder_path):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        if file.lower().endswith(('.md', '.markdown')):
                                            result = process_file(file_path, settings.OUTPUT_FOLDER)
                                            if result:
                                                processed_count += 1
                                            else:
                                                failed_count += 1
                                        else:
                                            skipped_count += 1
                                break
                            elif item_type == 'M' and 0 <= choice_index < len(matching_files):
                                # 处理选择的文件
                                file_path = matching_files[choice_index]
                                print(f"处理文件: {file_path}")
                                result = process_file(file_path, settings.OUTPUT_FOLDER)
                                if result:
                                    processed_count += 1
                                else:
                                    failed_count += 1
                                break
                            else:
                                print("无效的选择，请重新输入")
                        except ValueError:
                            print("请在类型字母后输入有效的数字")
                    except ValueError:
                        print("请输入有效的选择")
            
            # 只找到文件夹
            elif matching_folders:
                if len(matching_folders) == 1:
                    # 只有一个匹配的文件夹，直接处理
                    folder_path = matching_folders[0]
                    print(f"找到匹配的文件夹: {folder_path}")
                    # 处理文件夹中的所有Markdown文件
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if file.lower().endswith(('.md', '.markdown')):
                                result = process_file(file_path, settings.OUTPUT_FOLDER)
                                if result:
                                    processed_count += 1
                                else:
                                    failed_count += 1
                            else:
                                skipped_count += 1
                else:
                    # 多个匹配的文件夹，询问用户选择
                    print(f"找到多个匹配'{path}'的文件夹:")
                    for i, folder_path in enumerate(matching_folders, 1):
                        print(f"{i}. {folder_path}")
                    
                    # 获取用户选择
                    while True:
                        try:
                            choice = input("请选择要处理的文件夹编号（输入q退出）: ").strip()
                            if choice.lower() == 'q':
                                return
                            choice_index = int(choice) - 1
                            if 0 <= choice_index < len(matching_folders):
                                folder_path = matching_folders[choice_index]
                                break
                            else:
                                print("无效的选择，请重新输入")
                        except ValueError:
                            print("请输入有效的数字")
                    
                    # 处理选择的文件夹
                    print(f"处理文件夹: {folder_path}")
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if file.lower().endswith(('.md', '.markdown')):
                                result = process_file(file_path, settings.OUTPUT_FOLDER)
                                if result:
                                    processed_count += 1
                                else:
                                    failed_count += 1
                            else:
                                skipped_count += 1
            
            # 只找到文件
            elif matching_files:
                # 已有的文件处理逻辑
                if len(matching_files) == 1:
                    # 只有一个匹配项，直接处理
                    path = matching_files[0]
                    print(f"找到匹配文件: {path}")
                    if path.lower().endswith(('.md', '.markdown')):
                        result = process_file(path, settings.OUTPUT_FOLDER)
                        if result:
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        print(f"跳过非Markdown文件：{path}")
                        skipped_count += 1
                else:
                    # 多个匹配项，询问用户选择
                    print(f"找到多个匹配'{path}'的文件:")
                    for i, file_path in enumerate(matching_files, 1):
                        print(f"{i}. {file_path}")
                    
                    # 获取用户选择
                    while True:
                        try:
                            choice = input("请选择要处理的文件编号（输入q退出）: ").strip()
                            if choice.lower() == 'q':
                                return
                            choice_index = int(choice) - 1
                            if 0 <= choice_index < len(matching_files):
                                path = matching_files[choice_index]
                                break
                            else:
                                print("无效的选择，请重新输入")
                        except ValueError:
                            print("请输入有效的数字")
                    
                    # 处理选择的文件
                    print(f"处理文件: {path}")
                    if path.lower().endswith(('.md', '.markdown')):
                        result = process_file(path, settings.OUTPUT_FOLDER)
                        if result:
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        print(f"跳过非Markdown文件：{path}")
                        skipped_count += 1
            
            # 没有找到匹配项
            else:
                print(f"没有找到匹配'{path}'的文件或文件夹")
                return
    
    # 输出处理统计
    print(f"\n处理完成！统计信息：")
    print(f"- 成功处理的文件总数：{processed_count}")
    if updated_count > 0:
        print(f"- 已更新的文件数：{updated_count}")
    if unchanged_count > 0:
        print(f"- 未修改的文件数：{unchanged_count}")
    print(f"- 处理失败的文件数：{failed_count}")
    print(f"- 跳过的非Markdown文件数：{skipped_count}")