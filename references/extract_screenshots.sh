#!/usr/bin/env bash
#
# 真实截图截帧工具（铁律配套）
# 从剧集视频按真实时间戳批量截取画面帧，作为台词本插图。
# 严禁使用 AI 生成图片替代真实截图。
#
# 用法：
#   1) 单个时间点截帧
#      ./extract_screenshots.sh -i episode.mp4 -t 00:00:35 -o scene_01.jpg
#   2) 批量截帧（时间戳列表，每行一个，格式 时间戳<TAB>输出名）
#      ./extract_screenshots.sh -i episode.mp4 -l timestamps.txt -d ./scenes
#
set -euo pipefail

VIDEO=""
SINGLE_TS=""
SINGLE_OUT=""
LIST_FILE=""
OUT_DIR="."

usage() {
  cat <<'EOF'
用法:
  extract_screenshots.sh -i <视频文件> -t <时间戳> -o <输出图片>
  extract_screenshots.sh -i <视频文件> -l <时间戳列表文件> -d <输出目录>

参数:
  -i  剧集视频文件路径（必填）
  -t  单个时间戳，如 00:00:35 或 35
  -o  单张输出图片路径
  -l  时间戳列表文件，每行: "<时间戳><TAB或空格><输出文件名>"
  -d  批量输出目录，默认当前目录
  -h  显示帮助

说明:
  截帧时间点必须与该场景台词在剧中的实际位置一致，禁止近似或编造。
  质量参数 -q:v 2 输出高质量 JPEG。
EOF
}

while getopts "i:t:o:l:d:h" opt; do
  case "$opt" in
    i) VIDEO="$OPTARG" ;;
    t) SINGLE_TS="$OPTARG" ;;
    o) SINGLE_OUT="$OPTARG" ;;
    l) LIST_FILE="$OPTARG" ;;
    d) OUT_DIR="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$VIDEO" ]]; then
  echo "错误: 必须用 -i 指定视频文件。" >&2
  usage
  exit 1
fi

if [[ ! -f "$VIDEO" ]]; then
  echo "错误: 视频文件不存在: $VIDEO" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "错误: 未找到 ffmpeg，请先安装（macOS: brew install ffmpeg）。" >&2
  exit 1
fi

# 单个时间点截帧
if [[ -n "$SINGLE_TS" ]]; then
  if [[ -z "$SINGLE_OUT" ]]; then
    echo "错误: 单点截帧必须用 -o 指定输出图片路径。" >&2
    exit 1
  fi
  echo "截帧: $SINGLE_TS -> $SINGLE_OUT"
  ffmpeg -hide_banner -loglevel error -ss "$SINGLE_TS" -i "$VIDEO" \
    -frames:v 1 -q:v 2 -y "$SINGLE_OUT"
  echo "完成: $SINGLE_OUT"
  exit 0
fi

# 批量截帧
if [[ -n "$LIST_FILE" ]]; then
  if [[ ! -f "$LIST_FILE" ]]; then
    echo "错误: 时间戳列表文件不存在: $LIST_FILE" >&2
    exit 1
  fi
  mkdir -p "$OUT_DIR"
  while IFS= read -r line || [[ -n "$line" ]]; do
    # 跳过空行与注释行
    [[ -z "${line// }" ]] && continue
    [[ "$line" == \#* ]] && continue
    ts="$(echo "$line" | awk '{print $1}')"
    name="$(echo "$line" | awk '{print $2}')"
    if [[ -z "$ts" || -z "$name" ]]; then
      echo "跳过格式异常行: $line" >&2
      continue
    fi
    out="$OUT_DIR/$name"
    echo "截帧: $ts -> $out"
    ffmpeg -hide_banner -loglevel error -ss "$ts" -i "$VIDEO" \
      -frames:v 1 -q:v 2 -y "$out"
  done < "$LIST_FILE"
  echo "批量截帧完成，输出目录: $OUT_DIR"
  exit 0
fi

echo "错误: 请用 -t（单点）或 -l（批量）指定时间戳。" >&2
usage
exit 1
