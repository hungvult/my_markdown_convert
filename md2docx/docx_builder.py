"""
Trình dựng tài liệu DOCX chuẩn hóa (DOCX Document Builder)
Triển khai toàn bộ quy chuẩn định dạng ĐATN:
- Quản lý Section 1 (Bìa/Phụ bìa), Section 2 (Front Matter), Section 3 (Body)
- Format chuẩn: Times New Roman, 13pt, 1.2 line spacing, thụt đầu dòng 1cm, căn đều (Justified)
- Đánh số và căn vị trí bảng (trên), hình ảnh (dưới), công thức toán
- Chèn Mục lục tự động, Danh mục Bảng, Danh mục Hình
"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from .config import (
    FONT_FAMILY, COLOR_BLACK,
    BODY_FONT_SIZE, BODY_LINE_SPACING, BODY_FIRST_LINE_INDENT, BODY_ALIGNMENT,
    BODY_SPACE_BEFORE, BODY_SPACE_AFTER,
    H1_FONT_SIZE, H1_BOLD, H1_ALIGNMENT, H1_SPACE_BEFORE, H1_SPACE_AFTER,
    H2_FONT_SIZE, H2_BOLD, H2_ALIGNMENT, H2_SPACE_BEFORE, H2_SPACE_AFTER,
    H3_FONT_SIZE, H3_BOLD, H3_ALIGNMENT, H3_SPACE_BEFORE, H3_SPACE_AFTER,
    CAPTION_FONT_SIZE, CAPTION_ALIGNMENT, CAPTION_SPACE_BEFORE, CAPTION_SPACE_AFTER,
    TABLE_ALIGNMENT, TABLE_HEADER_BG, TABLE_BORDER_COLOR
)
from .section_manager import SectionManager
from .cover_generator import CoverGenerator
from .indexer import DocIndexer

class DocxReportBuilder:
    def __init__(self, metadata: dict, indexer: DocIndexer, base_dir: str = "."):
        self.metadata = metadata
        self.indexer = indexer
        self.base_dir = base_dir
        self.doc = Document()
        
        # State tracking
        self.current_section_idx = 1 # 1: Cover, 2: Front Matter, 3: Body
        self.body_started = False
        self.front_matter_started = False
        self.first_chapter_rendered = False

    def initialize_document(self):
        """Khởi tạo tài liệu và tạo trang bìa, phụ bìa"""
        # Section 1: Trang bìa
        s1 = SectionManager.setup_cover_section(self.doc)
        CoverGenerator.apply_cover_border(s1)
        
        # Render Bìa chính
        CoverGenerator.render_cover_page(self.doc, self.metadata, is_subcover=False)
        self.doc.add_page_break()
        
        # Render Phụ bìa
        CoverGenerator.render_cover_page(self.doc, self.metadata, is_subcover=True)

    def ensure_front_matter_section(self):
        """Chuyển sang Section 2: Lời cảm ơn, Mục lục, Danh mục"""
        if not self.front_matter_started:
            SectionManager.add_front_matter_section(self.doc)
            self.front_matter_started = True
            self.current_section_idx = 2

    def ensure_body_section(self):
        """Chuyển sang Section 3: Nội dung chính (Chương 1 trở đi)"""
        if not self.body_started:
            SectionManager.add_body_section(self.doc)
            self.body_started = True
            self.current_section_idx = 3

    def add_toc_field(self, paragraph):
        """Nhúng trường TOC (Table of Contents) tự động của Word"""
        p = paragraph._p
        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>' % nsdecls('w'))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        p.append(fldChar1)
        p.append(instrText)
        p.append(fldChar2)
        p.append(fldChar3)

    def render_heading(self, level: int, info: dict):
        """Render tiêu đề chuẩn theo level và outlineLvl"""
        h_type = info.get("type", "heading")
        text = info.get("display", "")

        # Quản lý chuyển đổi Section
        if h_type == "front_matter":
            self.ensure_front_matter_section()
            if self.front_matter_started and self.doc.paragraphs and len(self.doc.paragraphs) > 2:
                self.doc.add_page_break()
        elif h_type in ("chapter", "special_body"):
            self.ensure_body_section()
            if self.first_chapter_rendered:
                self.doc.add_page_break()
            self.first_chapter_rendered = True

        p = self.doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()

        if level == 1:
            p.alignment = H1_ALIGNMENT
            p.paragraph_format.space_before = H1_SPACE_BEFORE
            p.paragraph_format.space_after = H1_SPACE_AFTER
            p.paragraph_format.keep_with_next = True
            # Outline level 0
            pPr.append(parse_xml(r'<w:outlineLvl %s w:val="0"/>' % nsdecls('w')))
            
            run = p.add_run(text)
            run.font.name = FONT_FAMILY
            run.font.size = H1_FONT_SIZE
            run.font.bold = H1_BOLD
            run.font.color.rgb = COLOR_BLACK

            # Tự động sinh danh mục hình / bảng nếu gặp tiêu đề danh mục
            if "DANH MỤC HÌNH" in text.upper() or "DANH MỤC CÁC HÌNH" in text.upper():
                self.render_figures_catalog_table()
            elif "DANH MỤC BẢNG" in text.upper() or "DANH MỤC CÁC BẢNG" in text.upper():
                self.render_tables_catalog_table()
            elif "MỤC LỤC" in text.upper():
                p_toc = self.doc.add_paragraph()
                self.add_toc_field(p_toc)

        elif level == 2:
            self.ensure_body_section()
            p.alignment = H2_ALIGNMENT
            p.paragraph_format.space_before = H2_SPACE_BEFORE
            p.paragraph_format.space_after = H2_SPACE_AFTER
            p.paragraph_format.keep_with_next = True
            pPr.append(parse_xml(r'<w:outlineLvl %s w:val="1"/>' % nsdecls('w')))

            run = p.add_run(text)
            run.font.name = FONT_FAMILY
            run.font.size = H2_FONT_SIZE
            run.font.bold = H2_BOLD
            run.font.color.rgb = COLOR_BLACK

        elif level == 3:
            self.ensure_body_section()
            p.alignment = H3_ALIGNMENT
            p.paragraph_format.space_before = H3_SPACE_BEFORE
            p.paragraph_format.space_after = H3_SPACE_AFTER
            p.paragraph_format.keep_with_next = True
            pPr.append(parse_xml(r'<w:outlineLvl %s w:val="2"/>' % nsdecls('w')))

            run = p.add_run(text)
            run.font.name = FONT_FAMILY
            run.font.size = H3_FONT_SIZE
            run.font.bold = H3_BOLD
            run.font.color.rgb = COLOR_BLACK

        return p

    def render_paragraph(self, raw_text: str):
        """
        Render đoạn văn bản:
        - Times New Roman 13pt
        - Dãn dòng 1.2
        - Thụt đầu dòng 1cm
        - Căn đều (Justify)
        - Resolve tham chiếu chéo
        """
        text = self.indexer.resolve_cross_references(raw_text.strip())
        if not text:
            return None

        p = self.doc.add_paragraph()
        p.alignment = BODY_ALIGNMENT
        p.paragraph_format.line_spacing = BODY_LINE_SPACING
        p.paragraph_format.first_line_indent = BODY_FIRST_LINE_INDENT
        p.paragraph_format.space_before = BODY_SPACE_BEFORE
        p.paragraph_format.space_after = BODY_SPACE_AFTER

        self._render_inline_formatting(p, text)
        return p

    def render_figure(self, img_path: str, full_caption: str):
        """
        Render ảnh và Caption:
        - Ảnh căn giữa, tự co giãn theo chiều rộng trang
        - Caption nằm PHÍA DƯỚI ảnh: 'Hình X.Y. <Tên hình>' (in đậm, nghiêng)
        """
        resolved_caption = self.indexer.resolve_cross_references(full_caption)
        
        # Tìm file ảnh
        full_img_path = img_path
        if not os.path.isabs(img_path):
            full_img_path = os.path.join(self.base_dir, img_path)
        
        if os.path.exists(full_img_path):
            p_img = self.doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            
            run_img = p_img.add_run()
            # Giới hạn chiều rộng tối đa 15.5 cm để vừa lề
            try:
                run_img.add_picture(full_img_path, width=Cm(14.5))
            except Exception:
                run_img.add_picture(full_img_path)
        else:
            p_err = self.doc.add_paragraph()
            p_err.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p_err.add_run(f"[KHÔNG TÌM THẤY ẢNH: {img_path}]")
            r.font.color.rgb = RGBColor(255, 0, 0)
            r.font.bold = True

        # Caption nằm DƯỚI hình
        p_cap = self.doc.add_paragraph()
        p_cap.alignment = CAPTION_ALIGNMENT
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        
        # Tách 'Hình X.Y.' in đậm, phần còn lại in nghiêng
        m = re.match(r'^(Hình\s+\d+\.\d+\.?)(.*)$', resolved_caption)
        if m:
            r_bold = p_cap.add_run(m.group(1))
            r_bold.font.name = FONT_FAMILY
            r_bold.font.size = CAPTION_FONT_SIZE
            r_bold.font.bold = True
            
            r_text = p_cap.add_run(m.group(2))
            r_text.font.name = FONT_FAMILY
            r_text.font.size = CAPTION_FONT_SIZE
            r_text.font.italic = True
        else:
            r = p_cap.add_run(resolved_caption)
            r.font.name = FONT_FAMILY
            r.font.size = CAPTION_FONT_SIZE
            r.font.bold = True

    def render_table(self, rows_data: list, full_caption: str):
        """
        Render bảng và Caption:
        - Caption nằm PHÍA TRÊN bảng: 'Bảng X.Y. <Tên bảng>'
        - Format bảng: Header có background màu nhạt, viền xám, text căn giữa/trái
        """
        if full_caption:
            resolved_caption = self.indexer.resolve_cross_references(full_caption)
            p_cap = self.doc.add_paragraph()
            p_cap.alignment = CAPTION_ALIGNMENT
            p_cap.paragraph_format.space_before = Pt(8)
            p_cap.paragraph_format.space_after = Pt(3)
            p_cap.paragraph_format.keep_with_next = True
            
            m = re.match(r'^(Bảng\s+\d+\.\d+\.?)(.*)$', resolved_caption)
            if m:
                r_bold = p_cap.add_run(m.group(1))
                r_bold.font.name = FONT_FAMILY
                r_bold.font.size = CAPTION_FONT_SIZE
                r_bold.font.bold = True
                
                r_text = p_cap.add_run(m.group(2))
                r_text.font.name = FONT_FAMILY
                r_text.font.size = CAPTION_FONT_SIZE
                r_text.font.italic = True
            else:
                r = p_cap.add_run(resolved_caption)
                r.font.name = FONT_FAMILY
                r.font.size = CAPTION_FONT_SIZE
                r.font.bold = True

        if not rows_data:
            return

        num_rows = len(rows_data)
        num_cols = max(len(r) for r in rows_data) if rows_data else 0
        if num_cols == 0:
            return

        table = self.doc.add_table(rows=num_rows, cols=num_cols)
        table.alignment = TABLE_ALIGNMENT
        table.autofit = True

        # Viền bảng
        tblBorders = parse_xml(r'''
        <w:tblBorders %s>
          <w:top w:val="single" w:sz="4" w:space="0" w:color="%s"/>
          <w:left w:val="single" w:sz="4" w:space="0" w:color="%s"/>
          <w:bottom w:val="single" w:sz="4" w:space="0" w:color="%s"/>
          <w:right w:val="single" w:sz="4" w:space="0" w:color="%s"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="%s"/>
          <w:insideV w:val="single" w:sz="4" w:space="0" w:color="%s"/>
        </w:tblBorders>
        ''' % (nsdecls('w'), TABLE_BORDER_COLOR, TABLE_BORDER_COLOR, TABLE_BORDER_COLOR,
               TABLE_BORDER_COLOR, TABLE_BORDER_COLOR, TABLE_BORDER_COLOR))
        table._tbl.tblPr.append(tblBorders)

        for r_idx, row in enumerate(rows_data):
            docx_row = table.rows[r_idx]
            # Tránh ngắt giữa hàng khi sang trang
            trPr = docx_row._tr.get_or_add_trPr()
            trPr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
            
            is_header = (r_idx == 0)
            if is_header:
                trPr.append(parse_xml(r'<w:tblHeader %s/>' % nsdecls('w')))

            for c_idx, cell_value in enumerate(row):
                if c_idx < num_cols:
                    cell = docx_row.cells[c_idx]
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    
                    if is_header:
                        tcPr = cell._tc.get_or_add_tcPr()
                        shd = parse_xml(r'<w:shd %s w:val="clear" w:color="auto" w:fill="%s"/>' % (nsdecls('w'), TABLE_HEADER_BG))
                        tcPr.append(shd)

                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.15
                    
                    resolved_cell = self.indexer.resolve_cross_references(str(cell_value))
                    self._render_inline_formatting(p, resolved_cell, is_table_header=is_header)

        # Khoảng cách sau bảng
        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(6)

    def render_equation(self, formula_text: str, eq_label: str):
        """
        Render phương trình căn giữa kèm nhãn số (Chương.STT) ở lề phải
        Dùng bảng ẩn viền 1 hàng 2 cột
        """
        table = self.doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Cột 1: 14cm (công thức căn giữa)
        # Cột 2: 2cm (nhãn số căn phải)
        col_widths = [Cm(13.5), Cm(2.5)]
        for i, cell in enumerate(table.rows[0].cells):
            cell.width = col_widths[i]
            # Xóa viền cell
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'''
                <w:tcBorders %s>
                    <w:top w:val="none"/>
                    <w:left w:val="none"/>
                    <w:bottom w:val="none"/>
                    <w:right w:val="none"/>
                </w:tcBorders>
            ''' % nsdecls('w'))
            tcPr.append(tcBorders)

        # Cột công thức
        c1 = table.rows[0].cells[0]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(formula_text)
        r1.font.name = "Cambria Math"
        r1.font.size = Pt(12)
        r1.font.italic = True

        # Cột nhãn
        c2 = table.rows[0].cells[1]
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = p2.add_run(eq_label)
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12)
        r2.font.bold = True

    def render_figures_catalog_table(self):
        """Tự động sinh bảng danh mục hình ảnh từ catalog đã index"""
        if not self.indexer.figures_catalog:
            return
        
        rows = [["Số hiệu", "Tên hình ảnh", "Trang"]]
        for f in self.indexer.figures_catalog:
            rows.append([f["label"], f["caption"], "--"])
        self.render_table(rows, full_caption="")

    def render_tables_catalog_table(self):
        """Tự động sinh bảng danh mục bảng biểu từ catalog đã index"""
        if not self.indexer.tables_catalog:
            return
            
        rows = [["Số hiệu", "Tên bảng biểu", "Trang"]]
        for t in self.indexer.tables_catalog:
            rows.append([t["label"], t["caption"], "--"])
        self.render_table(rows, full_caption="")

    def _render_inline_formatting(self, paragraph, text: str, is_table_header: bool = False):
        """Parse và tạo các run có format: **bold**, *italic*, `code`, link"""
        # Tokenizer regex đơn giản hóa để phân tách văn bản inline
        pattern = r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))'
        tokens = re.split(pattern, text)

        for tok in tokens:
            if not tok:
                continue

            if tok.startswith("**") and tok.endswith("**"):
                r = paragraph.add_run(tok[2:-2])
                r.bold = True
            elif tok.startswith("*") and tok.endswith("*"):
                r = paragraph.add_run(tok[1:-1])
                r.italic = True
            elif tok.startswith("`") and tok.endswith("`"):
                r = paragraph.add_run(tok[1:-1])
                r.font.name = "Courier New"
                r.font.size = Pt(11)
            elif tok.startswith("[") and "](" in tok:
                m = re.match(r'\[(.*?)\]\((.*?)\)', tok)
                if m:
                    label, url = m.groups()
                    r = paragraph.add_run(label)
                    r.font.color.rgb = RGBColor(0, 102, 204)
                    r.underline = True
                else:
                    r = paragraph.add_run(tok)
            else:
                r = paragraph.add_run(tok)

            r.font.name = FONT_FAMILY
            r.font.size = BODY_FONT_SIZE if not is_table_header else Pt(12)
            if is_table_header:
                r.bold = True

    def save(self, output_path: str):
        """Lưu tài liệu DOCX kết quả"""
        self.doc.save(output_path)
