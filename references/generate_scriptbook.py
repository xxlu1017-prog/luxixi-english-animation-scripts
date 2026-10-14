#!/usr/bin/env python3
"""
儿童英语启蒙动画台词本 PDF 生成器
用法: python3 generate_scriptbook.py --data episode_data.json --output output.pdf
"""

import argparse
import json
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PAGE_WIDTH, PAGE_HEIGHT = A4
TOP_MARGIN = 0.55 * inch
BOTTOM_MARGIN = 0.55 * inch
LEFT_MARGIN = 0.55 * inch
RIGHT_MARGIN = 0.55 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
CONTENT_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

SPEAKER_COLORS = {
    "Bluey": "#1E88E5",
    "Bingo": "#FB8C00",
    "Bandit": "#43A047",
    "Chilli": "#E91E63",
    "Peppa": "#E53935",
    "George": "#42A5F5",
    "Mummy": "#E91E63",
    "Mum": "#E91E63",
    "Daddy": "#43A047",
    "Dad": "#43A047",
    "Madame Gazelle": "#6A1B9A",
    "Suzy": "#00897B",
    "Danny": "#6D4C41",
    "Freddy": "#FB8C00",
    "Pedro": "#00ACC1",
    "Emily": "#D81B60",
    "Mr. Elephant": "#D81B60",
    "Mr. Rabbit": "#7CB342",
    "Children": "#F4511E",
    "Parents": "#3949AB",
    "Narrator": "#757575",
    "Both": "#8E24AA",
    "All": "#F4511E",
    "Everyone": "#F4511E",
}

VOCAB_COLORS = {
    "high": "#C8E6C9",
    "mid": "#FFE0B2",
    "low": "#BBDEFB",
}

VOCAB_BORDER_COLORS = {
    "high": "#43A047",
    "mid": "#FB8C00",
    "low": "#1E88E5",
}


def register_cjk_font():
    import platform
    system = platform.system()
    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"]
    else:
        font_paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]

    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("CJKFont", font_path, subfontIndex=0))
            return "CJKFont"
    return "Helvetica"


def register_phonetic_font():
    import platform
    system = platform.system()
    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/Geneva.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        font_paths = ["C:/Windows/Fonts/arial.ttf"]
    else:
        font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("PhoneticFont", font_path))
            return "PhoneticFont"
    return "Helvetica"


def get_speaker_color(speaker):
    for key, color in SPEAKER_COLORS.items():
        if key.lower() in speaker.lower():
            return color
    return "#757575"


def compute_stats(data):
    """从实际数据计算统计数字：单词数=台词逐字稿总词数，高/中/低频词=词汇表各级别数量"""
    total_words = 0
    for scene in data.get('scenes', []):
        for d in scene.get('dialogues', []):
            total_words += len(d.get('text', '').split())
    vocab = data.get('vocabulary', [])
    high = sum(1 for v in vocab if v.get('level') == 'high')
    mid = sum(1 for v in vocab if v.get('level') == 'mid')
    low = sum(1 for v in vocab if v.get('level') == 'low')
    return total_words, high, mid, low


class VocabCard(Flowable):
    """词汇卡片"""
    def __init__(self, word, phonetic, pos, meaning, level, cjk_font="CJKFont", phonetic_font="PhoneticFont"):
        Flowable.__init__(self)
        self.word = word
        self.phonetic = phonetic
        self.pos = pos
        self.meaning = meaning
        self.level = level
        self.cjk_font = cjk_font
        self.phonetic_font = phonetic_font
        self.width = 2.45 * inch
        self.height = 0.44 * inch

    def draw(self):
        bg_color = VOCAB_COLORS.get(self.level, "#E0E0E0")
        border_color = VOCAB_BORDER_COLORS.get(self.level, "#9E9E9E")

        self.canv.setFillColor(HexColor(bg_color))
        self.canv.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        self.canv.setStrokeColor(HexColor(border_color))
        self.canv.setLineWidth(1.2)
        self.canv.roundRect(0, 0, self.width, self.height, 6, fill=0, stroke=1)

        self.canv.setFillColor(HexColor("#212121"))
        self.canv.setFont("Helvetica-Bold", 11)
        self.canv.drawString(7, self.height - 15, self.word)

        self.canv.setFont(self.phonetic_font, 8)
        self.canv.setFillColor(HexColor("#616161"))
        word_w = self.canv.stringWidth(self.word, "Helvetica-Bold", 11)
        self.canv.drawString(7 + word_w + 4, self.height - 15, f"[{self.phonetic}]")

        self.canv.setFont(self.cjk_font, 8.5)
        self.canv.setFillColor(HexColor("#424242"))
        self.canv.drawString(7, 7, f"{self.pos} {self.meaning}")


class SceneImage(Image):
    """场景插图：加载本地图片文件，带圆角边框效果"""
    def __init__(self, image_path, width=2.5*inch, height=1.75*inch):
        Image.__init__(self, image_path, width=width, height=height)
        self.hAlign = 'CENTER'


def get_styles(cjk_font):
    return {
        'title': ParagraphStyle(
            'Title', fontName=cjk_font, fontSize=20, leading=26,
            textColor=HexColor('#1a365d'), spaceAfter=4, alignment=TA_LEFT,
            wordWrap='CJK'
        ),
        'subtitle': ParagraphStyle(
            'Subtitle', fontName=cjk_font, fontSize=13, leading=17,
            textColor=HexColor('#2b6cb0'), spaceAfter=6, alignment=TA_LEFT,
            wordWrap='CJK'
        ),
        'body_small': ParagraphStyle(
            'BodySmall', fontName=cjk_font, fontSize=9, leading=14,
            textColor=HexColor('#4a5568'), wordWrap='CJK'
        ),
        'timestamp': ParagraphStyle(
            'Timestamp', fontName=cjk_font, fontSize=8, leading=10,
            textColor=HexColor('#90A4AE'), alignment=TA_LEFT, spaceBefore=2, spaceAfter=2
        ),
        'dialogue_text': ParagraphStyle(
            'DialogueText', fontName=cjk_font, fontSize=9.5, leading=13.5,
            textColor=HexColor('#212121'), wordWrap='CJK', spaceAfter=3
        ),
        'section_header': ParagraphStyle(
            'SectionHeader', fontName=cjk_font, fontSize=12, leading=16,
            textColor=HexColor('#2b6cb0'), spaceBefore=4, spaceAfter=5,
            wordWrap='CJK'
        ),
        'page_footer': ParagraphStyle(
            'PageFooter', fontName=cjk_font, fontSize=9, leading=12,
            textColor=HexColor('#90A4AE'), alignment=TA_CENTER
        ),
    }


def build_cover_page(data, cjk_font, phonetic_font, styles):
    """封面页：左侧大插图+核心词组，右侧核心词汇（第1页不放台词，避免与逐字稿重复）"""
    story = []

    title_text = f"{data['animation_name_cn']}台词本"
    story.append(Paragraph(title_text, styles['title']))

    subtitle_text = f"第{data['season']}季（{data['episode']:02d}）{data['episode_title']}"
    if data.get('episode_title_cn'):
        subtitle_text += f" {data['episode_title_cn']}"
    story.append(Paragraph(subtitle_text, styles['subtitle']))

    total_words, high, mid, low = compute_stats(data)
    stats_data = [[
        f"单词数: {total_words}",
        f"高频词: {high}",
        f"中频词: {mid}",
        f"低频词: {low}"
    ]]
    stats_table = Table(stats_data, colWidths=[CONTENT_WIDTH/4]*4, rowHeights=[0.3*inch])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), cjk_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#212121')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, 0), HexColor('#F5F5F5')),
        ('BACKGROUND', (1, 0), (1, 0), HexColor(VOCAB_COLORS['high'])),
        ('BACKGROUND', (2, 0), (2, 0), HexColor(VOCAB_COLORS['mid'])),
        ('BACKGROUND', (3, 0), (3, 0), HexColor(VOCAB_COLORS['low'])),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#BDBDBD')),
        ('INNERGRID', (0, 0), (-1, -1), 1, HexColor('#BDBDBD')),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 10))

    left_col = []
    right_col = []

    poster_path = data.get('poster_image', '')
    if poster_path and os.path.exists(poster_path):
        poster = SceneImage(poster_path, width=3.7*inch, height=3.7*inch*0.75)
        left_col.append(poster)
        left_col.append(Spacer(1, 10))

    phrases = data.get('phrases', [])
    if phrases:
        left_col.append(Paragraph("<b>核心词组</b>", styles['section_header']))
        for i, phrase in enumerate(phrases, 1):
            left_col.append(Paragraph(f"{i}. {phrase}", styles['body_small']))

    right_col.append(Paragraph("<b>核心词汇</b>", styles['section_header']))
    vocab_list = data.get('vocabulary', [])
    for v in vocab_list[:16]:
        card = VocabCard(
            v['word'], v['phonetic'], v['pos'], v['meaning'],
            v.get('level', 'mid'), cjk_font, phonetic_font
        )
        right_col.append(card)
        right_col.append(Spacer(1, 3))

    col_table = Table(
        [[left_col, right_col]],
        colWidths=[CONTENT_WIDTH * 0.56, CONTENT_WIDTH * 0.44]
    )
    col_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))
    story.append(col_table)

    return story


def build_content_pages(scenes, cjk_font, styles):
    """内容页：每个场景一行（左图右文），自然流动跨页"""
    story = []
    for i, scene in enumerate(scenes):
        story.append(KeepTogether(build_scene_row(scene, styles)))
        if i < len(scenes) - 1:
            story.append(Spacer(1, 12))
    return story


def build_scene_row(scene, styles):
    """单个场景行：左侧插图+时间戳，右侧彩色对话"""
    img_cell_w = 2.65 * inch
    img_w = 2.55 * inch

    left = []
    image_path = scene.get('image', '')
    if image_path and os.path.exists(image_path):
        left.append(SceneImage(image_path, width=img_w, height=img_w * 0.75))
    time_range = scene.get('time_range', '')
    if time_range:
        left.append(Paragraph(time_range, styles['timestamp']))

    right = []
    for d in scene.get('dialogues', []):
        speaker = d['speaker']
        text = d['text']
        translation = d.get('translation', '')
        color = get_speaker_color(speaker)

        dialogue_html = f"<font color='{color}'><b>{speaker}:</b></font> {text}"
        if translation:
            dialogue_html += f"<br/><font size='8' color='#78909C'>{translation}</font>"
        right.append(Paragraph(dialogue_html, styles['dialogue_text']))

    row = Table(
        [[left, right]],
        colWidths=[img_cell_w, CONTENT_WIDTH - img_cell_w]
    )
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 8),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return row


def generate_pdf(data_path, output_path):
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cjk_font = register_cjk_font()
    phonetic_font = register_phonetic_font()
    styles = get_styles(cjk_font)

    def draw_page_number(canv, doc):
        canv.saveState()
        canv.setFont(cjk_font, 8.5)
        canv.setFillColor(HexColor('#90A4AE'))
        canv.drawCentredString(PAGE_WIDTH / 2, 0.32 * inch, f"第 {doc.page} 页")
        canv.restoreState()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=f"{data['animation_name']} S{data['season']:02d}E{data['episode']:02d} 台词本",
        author="luxixi-english-animation-scripts"
    )

    story = []
    story.extend(build_cover_page(data, cjk_font, phonetic_font, styles))
    story.append(PageBreak())

    scenes = data.get('scenes', [])
    if scenes:
        story.extend(build_content_pages(scenes, cjk_font, styles))

    doc.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成儿童英语启蒙动画台词本 PDF")
    parser.add_argument("--data", required=True, help="JSON 数据文件路径")
    parser.add_argument("--output", required=True, help="输出 PDF 路径")
    args = parser.parse_args()

    generate_pdf(args.data, args.output)
