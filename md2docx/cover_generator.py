"""
Bộ sinh Trang bìa và Trang phụ bìa chuẩn ĐATN (Cover Generator)
Tuân thủ Phụ lục 1: Mẫu bìa Đồ án tốt nghiệp - ĐH Giao thông Vận tải
"""
import os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from .config import FONT_FAMILY

class CoverGenerator:
    @staticmethod
    def apply_cover_border(section):
        """Thêm khung viền đôi (Double Border) cho trang bìa"""
        borders = parse_xml(r'''
        <w:pgBorders %s w:offsetFrom="page">
          <w:top w:val="double" w:sz="12" w:space="24" w:color="000000"/>
          <w:left w:val="double" w:sz="12" w:space="24" w:color="000000"/>
          <w:bottom w:val="double" w:sz="12" w:space="24" w:color="000000"/>
          <w:right w:val="double" w:sz="12" w:space="24" w:color="000000"/>
        </w:pgBorders>
        ''' % nsdecls('w'))
        section._sectPr.append(borders)

    @classmethod
    def render_cover_page(cls, doc: Document, metadata: dict, is_subcover: bool = False):
        """
        Sinh 1 trang bìa hoặc phụ bìa
        """
        truong = metadata.get("truong", "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI").upper()
        khoa = metadata.get("khoa", "KHOA CÔNG NGHỆ THÔNG TIN").upper()
        de_tai = metadata.get("de_tai", "TÊN ĐỀ TÀI CỦA ĐỒ ÁN").upper()
        gvhd = metadata.get("gvhd", "TS. Nguyễn Văn A")
        svth = metadata.get("svth", "Nguyễn Văn B")
        mssv = metadata.get("mssv", "20123456")
        lop = metadata.get("lop", "CNTT 2 - K64")
        nam = metadata.get("nam", "2026")
        logo_path = metadata.get("logo_path", "assets/logo.jpg")

        # 1. Header trường & khoa
        p_truong = doc.add_paragraph()
        p_truong.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_truong.paragraph_format.space_before = Pt(0)
        p_truong.paragraph_format.space_after = Pt(4)
        r_truong = p_truong.add_run(truong)
        r_truong.font.name = FONT_FAMILY
        r_truong.font.size = Pt(14)
        r_truong.font.bold = True

        p_khoa = doc.add_paragraph()
        p_khoa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_khoa.paragraph_format.space_before = Pt(0)
        p_khoa.paragraph_format.space_after = Pt(18)
        r_khoa = p_khoa.add_run(khoa)
        r_khoa.font.name = FONT_FAMILY
        r_khoa.font.size = Pt(14)
        r_khoa.font.bold = True

        # 2. Logo trường
        resolved_logo = logo_path
        if resolved_logo and not os.path.exists(resolved_logo):
            fallback = os.path.join(os.path.dirname(__file__), "assets", "logo.jpg")
            if os.path.exists(fallback):
                resolved_logo = fallback

        if resolved_logo and os.path.exists(resolved_logo):
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.paragraph_format.space_before = Pt(6)
            p_logo.paragraph_format.space_after = Pt(18)
            run_logo = p_logo.add_run()
            run_logo.add_picture(resolved_logo, width=Inches(1.5))
        else:
            # Khoảng trống nếu không có ảnh logo
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_after = Pt(60)

        # 3. Tiêu đề ĐỒ ÁN TỐT NGHIỆP
        p_doan = doc.add_paragraph()
        p_doan.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_doan.paragraph_format.space_before = Pt(12)
        p_doan.paragraph_format.space_after = Pt(12)
        r_doan = p_doan.add_run("ĐỒ ÁN TỐT NGHIỆP")
        r_doan.font.name = FONT_FAMILY
        r_doan.font.size = Pt(20)
        r_doan.font.bold = True

        p_detai_label = doc.add_paragraph()
        p_detai_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_detai_label.paragraph_format.space_before = Pt(0)
        p_detai_label.paragraph_format.space_after = Pt(6)
        r_detai_label = p_detai_label.add_run("ĐỀ TÀI:")
        r_detai_label.font.name = FONT_FAMILY
        r_detai_label.font.size = Pt(14)
        r_detai_label.font.bold = True

        p_detai = doc.add_paragraph()
        p_detai.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_detai.paragraph_format.space_before = Pt(6)
        p_detai.paragraph_format.space_after = Pt(40)
        r_detai = p_detai.add_run(de_tai)
        r_detai.font.name = FONT_FAMILY
        r_detai.font.size = Pt(18)
        r_detai.font.bold = True
        r_detai.font.color.rgb = RGBColor(0, 32, 96) # Màu xanh Navy trang trọng

        # 4. Bảng thông tin sinh viên và giáo viên
        table = doc.add_table(rows=4, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Đặt độ rộng cột
        col_widths = [Cm(5.5), Cm(8.0)]
        for row in table.rows:
            for i, cell in enumerate(row.cells):
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

        info_data = [
            ("Giảng viên hướng dẫn:", f"{gvhd}"),
            ("Sinh viên thực hiện:", f"{svth}"),
            ("Lớp:", f"{lop}"),
            ("Mã sinh viên:", f"{mssv}")
        ]

        for i, (label, val) in enumerate(info_data):
            # Cột 1
            c1 = table.rows[i].cells[0]
            p1 = c1.paragraphs[0]
            p1.paragraph_format.space_before = Pt(2)
            p1.paragraph_format.space_after = Pt(2)
            r1 = p1.add_run(label)
            r1.font.name = FONT_FAMILY
            r1.font.size = Pt(13)
            r1.font.bold = True

            # Cột 2
            c2 = table.rows[i].cells[1]
            p2 = c2.paragraphs[0]
            p2.paragraph_format.space_before = Pt(2)
            p2.paragraph_format.space_after = Pt(2)
            r2 = p2.add_run(val)
            r2.font.name = FONT_FAMILY
            r2.font.size = Pt(13)

        # 5. Địa danh & Năm
        p_footer = doc.add_paragraph()
        p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_footer.paragraph_format.space_before = Pt(50)
        p_footer.paragraph_format.space_after = Pt(0)
        r_footer = p_footer.add_run(f"Hà Nội – {nam}")
        r_footer.font.name = FONT_FAMILY
        r_footer.font.size = Pt(13)
        r_footer.font.bold = True
