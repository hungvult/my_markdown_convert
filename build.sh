#!/bin/bash
# Script biên dịch Markdown sang DOCX chuẩn ĐATN
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="$DIR/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "[*] Đang khởi tạo môi trường ảo Python..."
    python3 -m venv "$DIR/.venv"
    "$DIR/.venv/bin/pip" install -r "$DIR/requirements.txt"
fi

INPUT="${1:-$DIR/template.md}"
OUTPUT="${2:-$DIR/Bao_Cao_Tot_Nghiep.docx}"
CONFIG="${3:-$DIR/thesis.yaml}"

echo "=========================================================="
echo "    BIÊN DỊCH BÁO CÁO ĐỒ ÁN TỐT NGHIỆP TỰ ĐỘNG"
echo "=========================================================="
echo "Input  : $INPUT"
echo "Output : $OUTPUT"
echo "Config : $CONFIG"
echo "----------------------------------------------------------"

PYTHONPATH="$DIR" "$PYTHON" -m md2docx.cli build "$INPUT" -o "$OUTPUT" -c "$CONFIG"

echo "=========================================================="
echo "Hoàn tất! File xuất tại: $OUTPUT"
echo "=========================================================="
