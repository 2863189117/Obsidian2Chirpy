# Obsidian2Chirpy 转换工具

Obsidian2Chirpy 是一个自动化工具，用于将 Obsidian 风格的 Markdown 笔记转换为兼容 Jekyll Chirpy 主题的博客文章格式。

## 功能特点

- 自动处理 Obsidian 格式的内部链接 (`[[链接]]`)，转换为斜体文本
- 将 Obsidian 的 Callout 语法转换为 Chirpy 主题的提示框格式
- 处理数学公式，确保与 Jekyll Chirpy 主题兼容
- 支持 YAML 前置元数据的自动生成和更新
- 使用AI自动生成文章摘要，添加到文章的description字段
- 自动检测和处理文件更新
- 支持批量处理整个文件夹的 Markdown 文件

## 安装要求

- Python 3.6+
- 支持的操作系统: macOS, Linux, Windows

## 使用方法

1. 克隆仓库到本地：

```bash
git clone https://github.com/2863189117/Obsidian2Chirpy.git
cd Obsidian2Chirpy
```

2. 配置设置:

编辑 `obsidian2chirpy/config/settings.py` 文件，设置您的 Obsidian 笔记源文件夹和 Jekyll 博客 _posts 文件夹的路径。

3. 运行转换:

```bash
# 处理单个文件
python main.py 路径/到/笔记.md

# 处理整个文件夹
python main.py 路径/到/文件夹

# 根据设置自动处理
python main.py

# 启用AI自动摘要生成
python main.py -s 路径/到/笔记.md
```

## 配置选项

在 `obsidian2chirpy/config/settings.py` 中可以设置以下选项：

- `OUTPUT_FOLDER`: 输出文件夹路径
- `POSTS_ROOT`: Jekyll 博客的 _posts 文件夹路径
- `SOURCE_FOLDER`: Obsidian 笔记源文件夹路径
- `CALLOUT_TYPE_MAPPING`: Callout 类型映射配置
- `AI_API_KEY`: 硅基流动AI API密钥
- `AI_MODEL`: 使用的AI模型名称
- `ENABLE_AUTO_SUMMARY`: 是否默认启用自动摘要
- `SUMMARY_MAX_LENGTH`: 摘要最大长度

## Callout 类型支持

工具已预定义以下 Callout 类型的转换规则:

- `info` → `.prompt-info`
- `tip` → `.prompt-tip`
- `warning` → `.prompt-warning`
- `danger` → `.prompt-danger`
- `quote` → `.prompt-quote`
- `question` → `.prompt-tip`
- `caution` → `.prompt-warning`

对于其它未定义的 Callout 类型，程序会询问用户如何处理。

## AI摘要生成功能

Obsidian2Chirpy支持使用AI自动为文章生成摘要，并将其添加到文章的YAML前置数据中的`description`字段。这将用于在博客首页和搜索引擎中显示文章摘要。

### 使用方法

1. 使用命令行参数启用AI摘要生成：

```bash
python main.py -s 路径/到/文件.md
# 或者
python main.py --summary 路径/到/文件夹
```

2. 首次运行时，如果未设置API密钥，程序会提示输入硅基流动AI API密钥。

### 配置选项

在`obsidian2chirpy/config/settings.py`中可以设置以下与AI摘要相关的选项：

- `AI_API_KEY`: 硅基流动AI API密钥
- `AI_API_URL`: API接口地址，默认为"https://api.lingyiwanwu.com/v1/chat/completions"
- `AI_MODEL`: 使用的AI模型，默认为"ERNIE-Bot-4"
- `ENABLE_AUTO_SUMMARY`: 是否默认启用自动摘要功能
- `SUMMARY_MAX_LENGTH`: 摘要最大长度，默认为150个字符

### 摘要示例

生成的摘要将作为`description`字段添加到文章YAML前置数据中，例如：

```yaml
---
title: "引力辐射(Weinberg)"
date: 2025-04-22 16:04:00 +0800
last_modified_at: 2025-05-11 19:06:26 +0800
description: "这篇文章探讨了广义相对论中的引力辐射，基于Weinberg的《引力与宇宙学》进行推导。分析了弱场近似下的Einstein场方程和辐射解，讨论了规范不变性和平面波解，并与电磁波进行了类比。"
categories: [Physics,GR]
math: true
tags: [note,"引力和宇宙学"]
---
```

## 版权和许可

© 2025 Pleiades

此项目根据 MIT 许可证开源，详细信息请参阅 LICENSE 文件。
