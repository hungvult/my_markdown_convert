#!/bin/bash
# Script biên dịch Markdown sang DOCX và PDF chuẩn ĐATN
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON="$DIR/.venv/bin/python"

# 1. Khởi tạo môi trường ảo nếu chưa có
if [ ! -f "$PYTHON" ]; then
    echo "[*] Đang khởi tạo môi trường ảo Python..."
    python3 -m venv "$DIR/.venv"
    "$DIR/.venv/bin/pip" install --upgrade pip
    "$DIR/.venv/bin/pip" install -r "$DIR/requirements.txt"
fi

# 2. Hàm hỗ trợ xuất PDF nếu có LibreOffice
convert_to_pdf() {
    local docx_path="$1"
    local target_dir
    target_dir="$(dirname "$docx_path")"
    if command -v libreoffice &> /dev/null; then
        echo "[*] Đang chuyển đổi sang PDF qua LibreOffice..."
        libreoffice --headless --convert-to pdf --outdir "$target_dir" "$docx_path" > /dev/null 2>&1 || true
        local pdf_path="${docx_path%.docx}.pdf"
        if [ -f "$pdf_path" ]; then
            echo "[THÀNH CÔNG] Đã tạo file PDF: $pdf_path"
        fi
    fi
}

build_target() {
    local input_path="$1"
    local output_path="$2"
    local config_path="${3:-}"

    echo "=========================================================="
    echo "    BIÊN DỊCH BÁO CÁO ĐỒ ÁN TỐT NGHIỆP TỰ ĐỘNG"
    echo "=========================================================="
    echo "Input  : $input_path"
    echo "Output : $output_path"
    if [ -n "$config_path" ]; then
        echo "Config : $config_path"
    fi
    echo "----------------------------------------------------------"

    local extra_args=()
    if [ -n "$config_path" ]; then
        extra_args+=("-c" "$config_path")
    fi

    PYTHONPATH="$DIR" "$PYTHON" -m md2docx.cli build "$input_path" -o "$output_path" "${extra_args[@]}"
    convert_to_pdf "$output_path"
    echo "=========================================================="
    echo "Hoàn tất! File xuất tại: $output_path"
    echo "=========================================================="
}

MODE="${1:-all}"

case "$MODE" in
    clean)
        echo "[*] Đang dọn dẹp thư mục out/..."
        rm -rf "$DIR/out"
        echo "[THÀNH CÔNG] Đã xóa thư mục out/"
        exit 0
        ;;
    single)
        build_target "$DIR/templates/single_file" "$DIR/out/single_file/output.docx"
        ;;
    multi)
        build_target "$DIR/templates/multi_chapter" "$DIR/out/multi_chapter/output.docx"
        ;;
    all)
        echo "[*] Biên dịch giải pháp 1: File đơn (single_file)..."
        build_target "$DIR/templates/single_file" "$DIR/out/single_file/output.docx"
        echo ""
        echo "[*] Biên dịch giải pháp 2: Đa chương (multi_chapter)..."
        build_target "$DIR/templates/multi_chapter" "$DIR/out/multi_chapter/output.docx"
        ;;
    *)
        # Chế độ truyền trực tiếp đường dẫn tùy biến
        CUSTOM_INPUT="$1"
        CUSTOM_OUTPUT="${2:-$DIR/out/output.docx}"
        CUSTOM_CONFIG="${3:-}"
        build_target "$CUSTOM_INPUT" "$CUSTOM_OUTPUT" "$CUSTOM_CONFIG"
        ;;
esac
