"""
Giao diện dòng lệnh CLI cho md2docx
Hỗ trợ:
- Chuyển đổi 1 file Markdown: python -m md2docx.cli build templates/single_file -o out/single_file/output.docx
- Chuyển đổi 1 thư mục chứa các chương: python -m md2docx.cli build templates/multi_chapter -o out/multi_chapter/output.docx
"""
import os
import sys
import argparse
import re
import yaml
from pathlib import Path
from bs4 import BeautifulSoup

from .parser import MarkdownDocParser
from .indexer import DocIndexer
from .docx_builder import DocxReportBuilder

def parse_args():
    parser = argparse.ArgumentParser(description="Chuyển đổi Markdown sang DOCX chuẩn Đồ án tốt nghiệp")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh thực thi")

    build_cmd = subparsers.add_parser("build", help="Biên dịch tài liệu Markdown sang DOCX")
    build_cmd.add_argument("input_path", help="Đường dẫn file .md hoặc thư mục chứa tài liệu/các chương")
    build_cmd.add_argument("-o", "--output", default="out/Bao_Cao_Tot_Nghiep.docx", help="Tên file DOCX đầu ra")
    build_cmd.add_argument("-c", "--config", default="", help="Đường dẫn file cấu hình metadata YAML (tự nhận diện nếu để trống)")
    build_cmd.add_argument("-b", "--bib", default="", help="Đường dẫn file BibTeX references.bib (tự nhận diện nếu để trống)")

    return parser.parse_args()

def find_project_root(input_path: str) -> Path:
    """Xác định thư mục gốc của bộ tài liệu (nơi chứa thesis.yaml, references.bib, assets/)"""
    path = Path(input_path).resolve()
    p = path.parent if path.is_file() else path

    # Nếu đang trỏ trực tiếp vào thư mục con 'chapters'
    if p.name == "chapters" and (p.parent / "thesis.yaml").exists():
        return p.parent
    if (p / "thesis.yaml").exists() or (p / "references.bib").exists():
        return p
    if (p / "chapters").is_dir():
        return p
    return p

def collect_markdown_files(input_path: str) -> list[str]:
    """Thu thập danh sách các file Markdown theo thứ tự tên"""
    path = Path(input_path).resolve()
    if path.is_file():
        return [str(path)]
    elif path.is_dir():
        # Ưu tiên 1: Thư mục con 'chapters'
        chapters_dir = path / "chapters"
        if chapters_dir.is_dir():
            files = sorted([str(f) for f in chapters_dir.glob("*.md") if not f.name.startswith(".")])
            if files:
                return files

        # Ưu tiên 2: Các file .md ngay tại thư mục chỉ định
        files = sorted([str(f) for f in path.glob("*.md") if not f.name.startswith(".")])
        if files:
            return files

        # Ưu tiên 3: File content.md hoặc template.md
        for candidate in ["content.md", "template.md"]:
            cand_path = path / candidate
            if cand_path.exists():
                return [str(cand_path)]

        return []
    else:
        raise FileNotFoundError(f"Không tìm thấy đường dẫn: {input_path}")

def load_metadata(config_path: str, frontmatter_meta: dict) -> dict:
    """Hợp nhất metadata từ file config và frontmatter"""
    meta = {
        "truong": "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI",
        "khoa": "KHOA CÔNG NGHỆ THÔNG TIN",
        "de_tai": "XÂY DỰNG HỆ THỐNG QUẢN LÝ DOANH NGHIỆP",
        "gvhd": "TS. Nguyễn Văn A",
        "svth": "Trần Văn B",
        "mssv": "20123456",
        "lop": "Công nghệ thông tin 2 - K64",
        "nam": "2026",
        "logo_path": "assets/logo.jpg"
    }

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                meta.update(cfg)
        except Exception as e:
            print(f"[CẢNH BÁO] Không đọc được file cấu hình {config_path}: {e}")

    # Frontmatter có độ ưu tiên cao hơn
    if frontmatter_meta:
        meta.update(frontmatter_meta)

    return meta

def run_pipeline(input_path: str, output_docx: str, config_path: str = "", bib_path: str = ""):
    """
    Quy trình biên dịch 2-pass:
    1. Parse Markdown và thu thập tokens.
    2. Pass 1: Indexer đăng ký Heading, Bảng, Hình, Phương trình, Trích dẫn BibTeX.
    3. Pass 2: DocxReportBuilder sinh tài liệu và resolve tham chiếu chéo / trích dẫn.
    """
    md_files = collect_markdown_files(input_path)
    if not md_files:
        print(f"[LỖI] Không có file Markdown nào tại: {input_path}")
        sys.exit(1)

    project_root = find_project_root(input_path)
    print(f"[*] Gốc dự án tài liệu: {project_root}")
    print(f"[*] Đang thu thập nội dung từ {len(md_files)} tệp Markdown...")
    raw_text_parts = []
    first_frontmatter = {}

    parser = MarkdownDocParser()

    for idx, fpath in enumerate(md_files):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            if idx == 0:
                first_frontmatter, content = parser.extract_frontmatter(content)
            else:
                _, content = parser.extract_frontmatter(content)
            raw_text_parts.append(content)

    full_markdown_text = "\n\n".join(raw_text_parts)

    # Tự động dò file config nếu không truyền
    if not config_path:
        for cand in [
            project_root / "thesis.yaml",
            Path(input_path).parent / "thesis.yaml",
            Path("thesis.yaml")
        ]:
            if cand.exists():
                config_path = str(cand)
                break

    # Metadata
    metadata = load_metadata(config_path, first_frontmatter)

    # Tự động nhận diện đường dẫn logo
    logo_val = metadata.get("logo_path", "assets/logo.jpg")
    if not os.path.isabs(logo_val):
        for cand in [
            project_root / logo_val,
            project_root / "assets" / Path(logo_val).name,
            Path(input_path).parent / logo_val,
            Path(__file__).parent / "assets" / "logo.jpg"
        ]:
            if cand.exists():
                metadata["logo_path"] = str(cand)
                break

    # Tokens
    tokens = parser.parse_to_tokens(full_markdown_text)

    # PASS 1: Indexing & Cataloging
    print("[*] Thực hiện Pass 1: Định chỉ mục, đánh số phân cấp cho Chương, Bảng, Hình, Công thức, Trích dẫn...")
    indexer = DocIndexer()

    # Tự động dò cơ sở dữ liệu BibTeX nếu không truyền
    if not bib_path:
        for cand in [
            project_root / "references.bib",
            Path(input_path).parent / "references.bib",
            Path("references.bib")
        ]:
            if cand.exists():
                bib_path = str(cand)
                break

    if bib_path and os.path.exists(bib_path):
        print(f"[*] Đang nạp cơ sở dữ liệu trích dẫn BibTeX: {bib_path}")
        indexer.load_bibtex(bib_path)

    # Phân tích sơ bộ để index
    i = 0
    token_count = len(tokens)
    heading_registrations = {} # token_index -> info
    table_registrations = {}   # table_open_index -> (caption_text, tbl_id, full_caption)
    figure_registrations = {}  # inline_img_index -> (full_caption, img_path)
    equation_registrations = {}# math_block_index -> (formula, eq_label)

    current_table_caption = None
    current_table_id = None

    while i < token_count:
        t = tokens[i]

        # Bắt caption bảng từ comment marker
        if t.type == "html_block" and "<!--TABLE_CAPTION:" in t.content:
            m = re.search(r'<!--TABLE_CAPTION:\s*(.*?)\s*\|\s*(tbl:[\w-]+)?-->', t.content)
            if m:
                current_table_caption = m.group(1).strip()
                current_table_id = m.group(2).strip() if m.group(2) else None
            i += 1
            continue

        # Bắt công thức toán từ marker
        if t.type == "html_block" and "<!--MATH_BLOCK:" in t.content:
            m = re.search(r'<!--MATH_BLOCK:\s*(.*?)\s*\|\s*(eq:[\w-]+)?-->', t.content, re.DOTALL)
            if m:
                formula = m.group(1).strip()
                eq_id = m.group(2).strip() if m.group(2) else None
                eq_label = indexer.register_equation(eq_id)
                equation_registrations[i] = (formula, eq_label)
            i += 1
            continue

        # Bắt bảng HTML từ html_block
        if t.type == "html_block" and "<table" in t.content.lower():
            soup = BeautifulSoup(t.content, "html.parser")
            table_tag = soup.find("table")
            if table_tag:
                cap = current_table_caption or ""
                tbl_id = current_table_id

                # Nếu chưa có caption, kiểm tra thẻ <caption> bên trong <table>
                if not cap:
                    caption_tag = table_tag.find("caption")
                    if caption_tag:
                        raw_caption = caption_tag.get_text(strip=True)
                        m_id = re.search(r'\{#(tbl:[\w-]+)\}', raw_caption)
                        if m_id:
                            tbl_id = m_id.group(1).strip()
                            cap = re.sub(r'\{#tbl:[\w-]+\}', '', raw_caption).strip()
                        else:
                            cap = raw_caption

                if cap.strip():
                    label, full_cap = indexer.register_table(cap, tbl_id)
                    table_registrations[i] = (cap, tbl_id, full_cap, "html", str(table_tag))
                else:
                    table_registrations[i] = ("", None, "", "html", str(table_tag))

                current_table_caption = None
                current_table_id = None
                i += 1
                continue

        # Bắt tiêu đề
        if t.type == "heading_open":
            level = int(t.tag[1]) # 'h1' -> 1
            title_text = tokens[i+1].content if (i+1 < token_count and tokens[i+1].type == "inline") else ""
            h_info = indexer.register_heading(level, title_text)
            heading_registrations[i] = h_info
            i += 2
            continue

        # Bắt bảng Markdown
        if t.type == "table_open":
            cap = current_table_caption or ""
            tbl_id = current_table_id
            if cap.strip():
                label, full_cap = indexer.register_table(cap, tbl_id)
                table_registrations[i] = (cap, tbl_id, full_cap, "markdown", None)
            else:
                table_registrations[i] = ("", None, "", "markdown", None)
            current_table_caption = None
            current_table_id = None
            i += 1
            continue

        # Bắt ảnh trong inline token & quét trích dẫn
        if t.type == "inline":
            # Quét các khóa trích dẫn BibTeX (@citekey)
            indexer.scan_citations(t.content)

            # Kiểm tra cú pháp ![Caption](path){#fig:id}
            img_pattern = r'!\[(.*?)\]\((.*?)\)(?:\{#(fig:[\w-]+)\})?'
            for match in re.finditer(img_pattern, t.content):
                caption = match.group(1).strip()
                img_path = match.group(2).strip()
                fig_id = match.group(3).strip() if match.group(3) else None
                label, full_cap = indexer.register_figure(caption, fig_id)
                figure_registrations[i] = (full_cap, img_path)

        i += 1

    # Kiểm toán cấu trúc tài liệu sau Pass 1
    indexer.audit_document()

    # PASS 2: Dựng tài liệu và resolve tham chiếu chéo
    print("[*] Thực hiện Pass 2: Dựng tài liệu DOCX và resolve tham chiếu chéo / trích dẫn...")
    builder = DocxReportBuilder(metadata=metadata, indexer=indexer, base_dir=str(project_root))
    builder.initialize_document()

    in_bib_section = False
    i = 0
    while i < token_count:
        t = tokens[i]

        # 1. Heading
        if t.type == "heading_open":
            level = int(t.tag[1])
            info = heading_registrations.get(i, {"level": level, "display": tokens[i+1].content})
            builder.render_heading(level, info)

            # Tự động kết xuất danh mục tài liệu tham khảo nếu có trích dẫn BibTeX
            if level == 1 and info.get("is_references"):
                in_bib_section = True
                if indexer.cited_entries:
                    for c_idx, entry in enumerate(indexer.cited_entries):
                        formatted = f"[{c_idx + 1}] " + indexer.format_bibliography_entry(entry, c_idx + 1)
                        builder.render_paragraph(formatted)
            else:
                if level == 1:
                    in_bib_section = False

            i += 3 # open, inline, close
            continue

        # 2. Equation Block
        if t.type == "html_block" and i in equation_registrations:
            formula, eq_label = equation_registrations[i]
            builder.render_equation(formula, eq_label)
            i += 1
            continue

        # 2b. HTML Table
        if t.type == "html_block" and i in table_registrations:
            reg = table_registrations[i]
            if len(reg) >= 5 and reg[3] == "html":
                _, _, full_cap, _, table_html = reg
                builder.render_html_table(table_html, full_cap)
                i += 1
                continue

        # 3. Figure
        if t.type == "paragraph_open" and (i+1 < token_count) and (i+1 in figure_registrations):
            full_cap, img_path = figure_registrations[i+1]
            builder.render_figure(img_path, full_cap)
            i += 3 # p_open, inline, p_close
            continue

        # 4. Table Markdown
        if t.type == "table_open":
            reg = table_registrations.get(i, ("", None, ""))
            full_cap = reg[2] if len(reg) >= 3 else ""
            # Thu thập hàng của bảng
            rows = []
            current_row = []
            i += 1
            while i < token_count and tokens[i].type != "table_close":
                tok = tokens[i]
                if tok.type in ("th_open", "td_open"):
                    cell_text = tokens[i+1].content if (i+1 < token_count and tokens[i+1].type == "inline") else ""
                    current_row.append(cell_text)
                    i += 2
                elif tok.type in ("tr_close",):
                    if current_row:
                        rows.append(current_row)
                        current_row = []
                    i += 1
                else:
                    i += 1

            builder.render_table(rows, full_cap)
            i += 1 # bỏ qua table_close
            continue

        # Bỏ qua list mẫu thủ công nếu đã tự động sinh danh mục tài liệu tham khảo từ BibTeX
        if in_bib_section and indexer.cited_entries and t.type in ("ordered_list_open", "bullet_list_open"):
            list_close_type = "ordered_list_close" if t.type == "ordered_list_open" else "bullet_list_close"
            while i < token_count and tokens[i].type != list_close_type:
                i += 1
            i += 1
            continue

        # 5. Regular Paragraph
        if t.type == "paragraph_open":
            p_text = tokens[i+1].content if (i+1 < token_count and tokens[i+1].type == "inline") else ""
            if p_text.strip():
                # Bỏ qua nếu là marker HTML
                if not p_text.startswith("<!--"):
                    # Nếu đã tự động sinh danh mục BibTeX thì bỏ qua các dòng đánh số mẫu thủ công trong mục tham khảo
                    if in_bib_section and indexer.cited_entries and re.match(r'^\d+\.\s*', p_text):
                        pass
                    else:
                        builder.render_paragraph(p_text)
            i += 3
            continue

        i += 1

    # Lưu kết quả
    builder.save(output_docx)
    print(f"[THÀNH CÔNG] Đã tạo file: {output_docx}")

def main():
    args = parse_args()
    if args.command == "build":
        run_pipeline(args.input_path, args.output, args.config, args.bib)
    else:
        print("Sử dụng lệnh: python -m md2docx.cli build <input_path> -o <output.docx>")

if __name__ == "__main__":
    main()
