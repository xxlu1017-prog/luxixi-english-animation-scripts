# luxixi-english-animation-scripts

> 从英语启蒙动画（如 Bluey、Peppa Pig、Paw Patrol）生成可直接打印的 **A4 彩色台词本 PDF**。

输入动画名称、季、集，即可产出一份包含「真实剧集截帧 + 角色彩色对话 + 中文翻译 + 核心词汇卡片」的学习材料，帮助儿童在观看动画的同时跟读台词、积累词汇。

## 特性

- **按观众蓝思值（Lexile）选词分级**：以目标读者的阅读水平为准（而非剧集本身难度）挑选核心词汇，并分高/中/低频三级。
- **真实剧集截帧**：所有插图均来自动画真实画面帧，**严禁使用 AI 生成图片**（铁律）。
- **角色彩色对话**：说话人按角色配色，英文台词 + 中文翻译逐行对照。
- **核心词汇卡片**：单词 + 国际音标 + 词性 + 中文释义，按难度分三级底色（绿/橙/蓝）。
- **自动统计**：封面统计条的单词数、高/中/低频词数由脚本从真实数据自动计算，禁止手写。

## 安装

```bash
git clone https://github.com/luxixi/english-animation-scripts.git
cd english-animation-scripts
pip install -r requirements.txt
```

> 提示：本仓库以 `luxixi` 组织名承载品牌前缀；若你 fork 或自行发布，仓库名可保持 `english-animation-scripts`。

## 依赖

- Python 3.8+
- `reportlab`（必需，用于生成 PDF）
- `Pillow`（可选，用于图片处理）
- `ffmpeg`（系统级，用于按时间戳截帧，需自行安装）

## 用法

### 1. 准备输入数据

按 `references/data_schema.json` 的结构准备一份 `episode_data.json`，至少包含动画名、季集、台词逐字稿（场景 + 时间戳 + 对话 + 中文翻译）、词汇表与核心词组。

### 2. 生成 PDF

```bash
python3 references/generate_scriptbook.py \
  --data episode_data.json \
  --output Bluey_S01E01.pdf
```

### 3. 提取真实截帧（可选但需要）

按场景真实时间戳批量截帧，需提前自行获取该集视频源：

```bash
# 单帧
./references/extract_screenshots.sh -i episode.mp4 -t 00:00:35 -o scene_01.jpg

# 批量（timestamps.txt 每行一个时间戳）
./references/extract_screenshots.sh -i episode.mp4 -l timestamps.txt -d ./scenes
```

## 数据格式（简例）

```json
{
  "animation_name": "Bluey",
  "animation_name_cn": "布鲁伊",
  "season": 1,
  "episode": 1,
  "episode_title": "The Magic Xylophone",
  "episode_title_cn": "神奇的木琴",
  "target_lexile": "200-300L",
  "poster_image": "/abs/path/to/scenes/scene_1.jpg",
  "vocabulary": [
    {"word": "magic", "phonetic": "ˈmædʒɪk", "pos": "n./adj.", "meaning": "魔法；魔术的", "level": "mid"}
  ],
  "phrases": ["take turns 轮流"],
  "scenes": [
    {
      "scene_id": 1,
      "scene_type": "living_room",
      "image": "/abs/path/to/scenes/scene_1.jpg",
      "time_range": "00:00 - 00:45",
      "dialogues": [
        {"speaker": "Bluey", "text": "Mum! Dad! Bingo! Bluey!", "translation": "妈妈！爸爸！宾果！布鲁伊！"}
      ]
    }
  ]
}
```

> 统计条数字（单词数、高/中/低频词数）无需在 JSON 中提供，脚本会自动计算。

## 目录结构

```
luxixi-english-animation-scripts/
├── SKILL.md                          # Skill 主说明（面向 Agent 的工作流）
├── README.md                         # 本文件
├── LICENSE                           # MIT 许可证
├── requirements.txt                  # Python 依赖
└── references/
    ├── generate_scriptbook.py        # PDF 生成主脚本
    ├── extract_screenshots.sh        # 真实截图截帧工具（ffmpeg 按时间戳批量截帧）
    └── data_schema.json              # 输入数据 JSON Schema
```

## 工作流程（概述）

1. **确定观众蓝思值** —— 已知则直接使用，未知则按年龄/年级估算并确认（未回应则默认 200-300L）。
2. **获取真实台词** —— 从字幕/剧本网站获取，逐句忠于原剧，禁止虚构。
3. **提取核心词汇** —— 按蓝思值选词并分三级。
4. **获取真实截帧** —— 自行搜索下载视频源，用 ffmpeg 按真实时间戳截帧，**禁止 AI 生成图**。
5. **生成 PDF** —— 运行 `generate_scriptbook.py`。

## 版权与免责声明

- 本仓库**仅包含生成工具与说明**，不打包、不包含任何受版权保护的动画视频、截图或台词文本。
- 工具产出的台词本涉及第三方动画的台词与画面，**仅限个人学习 / 教育用途**。请遵守你所在国家/地区的版权法与相关平台服务条款，自行确保获取动画资源的合法性。
- 动画名称、角色名等为其各自权利人的商标/版权财产，本工具不主张任何权利。

## 许可证

[MIT](LICENSE) © 2026 luxixi
