---
name: luxixi-english-animation-scripts
description: Generate A4 printable colorful English learning scriptbooks for children from English enlightenment animations. Input animation name, season, and episode to produce a PDF with scene illustrations, color-coded dialogue with speaker names, and core vocabulary cards. Use when user asks to create "台词本", "英语启蒙台词本", "儿童英语学习", or generate learning materials from animations like Bluey, Peppa Pig, etc.
version: 1.0.0
metadata:
  openclaw:
    author: luxixi
---

# 儿童英语启蒙动画台词本生成器

## 概述

将英语启蒙动画的某一集转化为 A4 可直接打印的彩色台词本 PDF，帮助儿童在观看动画的同时学习英语台词、积累词汇。

核心特点：选词难度以**观众（目标读者）的蓝思值**为准——观众可能已知自己的蓝思值，也可能不知道，工作流第一步会先确定该值，再据此选词与分级。

## 输入参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `animation_name` | 动画英文名称 | Bluey, Peppa Pig, Paw Patrol |
| `animation_name_cn` | 动画中文名称 | 布鲁伊, 小猪佩奇 |
| `season` | 第几季 | 1 |
| `episode` | 第几集 | 1 |
| `episode_title` | 单集英文标题 | The Magic Xylophone |
| `episode_title_cn` | 单集中文标题 | 神奇的木琴 |
| `target_lexile` | 观众蓝思值（可正式值或估算区间） | 250L，或"4-6岁初启蒙" |
| `output_path` | 输出 PDF 路径 | ./Bluey_S01E01.pdf |

## 适用范围与内容真实性（必须遵守）

1. **素材范围**：仅限常见儿童英语启蒙动漫，如布鲁伊（Bluey）、小猪佩奇（Peppa Pig）、汪汪队（Paw Patrol）、Journey to the West（西游记英文版）等常见启蒙书单内的作品。所有剧集均按同一套逻辑生成台词本。
2. **范围外先确认**：若用户输入的动漫不属于常见儿童启蒙动漫范围，必须先与用户确认后再生成，不得直接开工。
3. **禁止编造**：台词、时间戳、剧情必须来自该集真实内容（字幕/官方剧本）；禁止虚构对话或剧情。
4. **时间戳必须真实**：每个场景的时间范围必须落在该集实际时长内（如布鲁伊单集约 7 分钟，场景时间不得超出 07:00），并与该场景在剧中的实际位置对应。
5. **插图真实性（铁律，不可违反）**：台词本中的所有插图（封面主图 + 各场景图）必须使用该动画**真实剧集的截图（画面帧）**，**严禁使用 AI 生成图片**。视频源与截图由 Agent 自行解决——主动搜索并下载该集视频源，再用 ffmpeg 按真实时间戳截帧；**不得要求/等待用户提供视频**。仅在确实找不到任何可用视频源时，才向用户说明情况并请求提供。

## 产出物结构

### 封面页（第 1 页）
- **标题**：{动画中文名}台词本（如"布鲁伊台词本"、"小猪佩奇台词本"）
- **副标题**：第X季（XX）单集标题
- **统计条**：单词数 / 高频词 / 中频词 / 低频词
  - 数字必须由脚本从实际数据计算，禁止手写：单词数=台词逐字稿总词数，高/中/低频词=词汇表各级别的实际数量
- **左侧**：单集主插图 + 核心词组列表
- **右侧**：核心词汇卡片（单词+音标+词性+中文释义，按绿/橙/蓝分级底色）
- 第 1 页不放台词正文，避免与第 2 页起的逐字稿重复

### 内容页（第 2 页起）
- **台词逐字稿**，按场景分行排列：每行左侧场景插图 + 时间戳，右侧该场景全部对话
- 对话内容：说话人名彩色标注（Bluey=蓝色，Bingo=橙色，Bandit=绿色，Chilli=粉色），英文台词 + 中文翻译
- 每页底部居中页码

## 工作流程

### 第一步：了解观众的蓝思值（必须先做，选词的依据）

在选词之前，必须先确定目标读者（观众）的蓝思值区间。观众的蓝思值可能已知，也可能未知，分两种情况处理：

**情况 A：观众知道自己的蓝思值**
- 直接记录该值（或区间）作为 `target_lexile`，选词区间取该值 **−100L ~ +50L** 作为舒适区（略微低于读者水平更利于独立跟读）。
- 例：观众为 250L → 选词区间 150L-300L。

**情况 B：观众不知道蓝思值**
- 不要猜。主动向观众询问**年龄、年级、英语启蒙时长**三项信息，再按下表估算，并把估算结果回告观众确认后再继续：

  | 观众情况 | 估算蓝思值 | 说明 |
  |---------|-----------|------|
  | 3-4 岁，尚未启蒙 | BR-150L | 以单词、拟声跟读为主 |
  | 4-6 岁，初启蒙（默认） | 200-300L | 最常见区间 |
  | 6-8 岁，有基础 | 300-450L | 可读短句、常见时态 |
  | 8-10 岁，进阶 | 450-600L | 可挑战长句与复句 |

- 也可提示观众用「美国年级—蓝思对照表」自评（如美国 1 年级约 200-400L、2 年级约 300-500L）。
- **观众不回答、或未提供、或明确表示不知道/不方便提供** → 不再等待，直接默认按 **200-300L（4-6 岁初启蒙）** 继续生成，并在交付时说明本套台词本采用的区间。

**注意**：无论走情况 A 还是情况 B，都必须先确定 `target_lexile` 才能进入选词。情况 B 中若观众未回应，即以默认值 **200-300L** 填入后正常继续，不得因等待回复而卡住流程。

### 第二步：获取台词数据

从以下来源获取该集的完整台词：
1. 搜索动画字幕网站（如 opensubtitles, subscene）
2. 搜索动画台词本/剧本（如 genius.com, springfieldspringfield）
3. 台词必须逐句忠于真实剧集，禁止根据梗概虚构或改写对话；若确实找不到完整台词，须向用户说明，不得编造

### 第三步：提取核心词汇

从台词中提取适合儿童学习的核心词汇，**难度以第一步确定的 `target_lexile` 为准**：
- **蓝思值适配**：以 `target_lexile` 区间选词；优先选取落在该区间内的高频动词、名词、形容词（如 freeze, turn, pretend）
- **兼顾剧集本身蓝思**：若该剧集本身蓝思高于观众区间，只保留区间内的词；超出区间的剧集主题词（如 xylophone, squabble）标记为低频/进阶词，供家长选讲
- 每个词汇包含：单词、国际音标、词性缩写、中文释义
- 按**相对于观众蓝思值的难度**分三级：高频词（绿色，最贴区间下沿、最常出现）、中频词（橙色）、低频词（蓝色，接近或略高于区间上沿）

### 第四步：获取真实场景截图（铁律，禁止用 AI 生成图替代）

为每个关键对话场景获取该集的**真实画面截图**：
1. **自行解决视频源**：主动搜索该集的视频源（官方 YouTube 频道、可下载资源等）并下载到本地；不得要求/等待用户提供视频。
2. **按真实时间戳截帧**：用 ffmpeg 按该场景在剧中的真实时间戳截取画面帧：

   ```bash
   ffmpeg -ss <时间戳> -i <视频文件> -frames:v 1 -q:v 2 scene_XX.jpg
   ```

   批量截帧可调用 `references/extract_screenshots.sh`。
3. **时间必须准确**：截图时间点必须与该场景台词在剧中出现的实际位置一致，禁止近似或编造。
4. **禁止 AI 生成**：不得用 AI 生图、简笔画或任何合成图替代真实截图。
5. 仅在确实找不到任何可用视频源时，才向用户说明情况并请求提供。

### 第五步：排版生成 PDF

使用 `generate_scriptbook.py` 脚本生成 PDF：

```bash
python3 references/generate_scriptbook.py \
  --data /path/to/episode_data.json \
  --output /path/to/output.pdf
```

### 数据格式（JSON）

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
    {"word": "magic", "phonetic": "ˈmædʒɪk", "pos": "n./adj.", "meaning": "魔法；魔术的", "level": "mid"},
    ...
  ],
  "phrases": [
    "Rondo Alla Turca 土耳其进行曲",
    "take turns 轮流",
    ...
  ],
  "scenes": [
    {
      "scene_id": 1,
      "scene_type": "living_room",
      "image": "/abs/path/to/scenes/scene_1.jpg",
      "time_range": "00:00 - 00:45",
      "dialogues": [
        {"speaker": "Bluey", "text": "Mum! Dad! Bingo! Bluey!", "translation": "妈妈！爸爸！宾果！布鲁伊！"},
        {"speaker": "Bandit", "text": "Ladies and gentlemen...", "translation": "女士们先生们..."}
      ]
    },
    ...
  ]
}
```

注意：统计条数字（单词数、高/中/低频词数）不需要在 JSON 中提供，脚本会自动从 scenes 和 vocabulary 计算。

## 颜色规范

角色颜色按动画适配，脚本 `SPEAKER_COLORS` 已内置以下常见角色：

| 动画 | 角色 | 颜色 | Hex |
|------|------|------|-----|
| 布鲁伊 | Bluey | 蓝色 | #1E88E5 |
| 布鲁伊 | Bingo | 橙色 | #FB8C00 |
| 布鲁伊 | Bandit / Dad | 绿色 | #43A047 |
| 布鲁伊 | Chilli / Mum | 粉色 | #E91E63 |
| 小猪佩奇 | Peppa | 红色 | #E53935 |
| 小猪佩奇 | George | 浅蓝 | #42A5F5 |
| 小猪佩奇 | Mummy Pig | 粉色 | #E91E63 |
| 小猪佩奇 | Daddy Pig | 绿色 | #43A047 |
| 通用 | Narrator / 旁白 | 灰色 | #757575 |

新动画的角色按"主角色鲜明、家人与现有家人色一致"的原则向 `SPEAKER_COLORS` 添加。

## 词汇级别颜色

| 级别 | 底色 | 用途 |
|------|------|------|
| 高频词 | 浅绿 #C8E6C9 | 最常用词汇 |
| 中频词 | 浅橙 #FFE0B2 | 常用词汇 |
| 低频词 | 浅蓝 #BBDEFB | 进阶词汇 |

## 依赖

- Python 3.8+
- reportlab
- Pillow（可选，用于图片处理）

## 文件结构

```
luxixi-english-animation-scripts/
├── SKILL.md                          # 本文件
└── references/
    ├── generate_scriptbook.py        # PDF 生成主脚本
    ├── extract_screenshots.sh        # 真实截图截帧工具（ffmpeg 按时间戳批量截帧）
    └── data_schema.json              # 输入数据 JSON Schema
```
