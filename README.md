# Obsidian2Chirpy 转换工具

Obsidian2Chirpy 是一个自动化工具，用于将 Obsidian 风格的 Markdown 笔记转换为兼容 Jekyll Chirpy 主题的博客文章格式。

## 功能特点

- 自动处理 Obsidian 格式的内部链接 (`[[链接]]`)，转换为斜体文本
- 将 Obsidian 的 Callout 语法转换为 Chirpy 主题的提示框格式
- 处理数学公式，确保与 Jekyll Chirpy 主题兼容
- 支持 YAML 前置元数据的自动生成和更新
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
```

## 配置选项

在 `obsidian2chirpy/config/settings.py` 中可以设置以下选项：

- `OUTPUT_FOLDER`: 输出文件夹路径
- `POSTS_ROOT`: Jekyll 博客的 _posts 文件夹路径
- `SOURCE_FOLDER`: Obsidian 笔记源文件夹路径
- `CALLOUT_TYPE_MAPPING`: Callout 类型映射配置

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

## 版权和许可

© 2025 Pleiades

此项目根据 MIT 许可证开源，详细信息请参阅 LICENSE 文件。
