"""
Bộ quản lý phân đoạn văn bản OOXML (Section Manager)
Thiết lập 3 Section chuyên biệt:
- Section 1: Trang bìa chính & phụ bìa (Không Header, Không Footer)
- Section 2: Lời cảm ơn, Mục lục, Danh mục hình/bảng (Đánh số La Mã thường hoặc không số)
- Section 3: Nội dung chính từ Chương 1 đến hết (Đánh số trang 1, 2, 3... ở Header căn giữa)
"""
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from .config import (
    PAGE_WIDTH, PAGE_HEIGHT,
    MARGIN_TOP, MARGIN_BOTTOM, MARGIN_LEFT, MARGIN_RIGHT,
    FONT_FAMILY
)

class SectionManager:
    @staticmethod
    def apply_page_margins(section):
        """Thiết lập kích thước khổ giấy A4 và lề chuẩn"""
        section.page_width = PAGE_WIDTH
        section.page_height = PAGE_HEIGHT
        section.top_margin = MARGIN_TOP
        section.bottom_margin = MARGIN_BOTTOM
        section.left_margin = MARGIN_LEFT
        section.right_margin = MARGIN_RIGHT

    @classmethod
    def setup_cover_section(cls, doc: Document):
        """Khởi tạo Section 1: Trang bìa (không header/footer)"""
        s1 = doc.sections[0]
        cls.apply_page_margins(s1)
        s1.header.is_linked_to_previous = False
        s1.footer.is_linked_to_previous = False
        return s1

    @classmethod
    def add_front_matter_section(cls, doc: Document):
        """
        Tạo Section 2: Lời cảm ơn, Mục lục và danh mục
        - Bắt đầu đánh số trang từ 1 ở GIỮA, ĐỈNH TRANG (Header Center)
        """
        s2 = doc.add_section(WD_SECTION.NEW_PAGE)
        cls.apply_page_margins(s2)
        s2.header.is_linked_to_previous = False
        s2.footer.is_linked_to_previous = False

        # Cấu hình số trang bắt đầu từ 1
        sectPr = s2._sectPr
        for child in list(sectPr):
            if child.tag.endswith('pgNumType') or child.tag.endswith('pgBorders'):
                sectPr.remove(child)
        pgNumType = parse_xml(r'<w:pgNumType %s w:start="1"/>' % nsdecls('w'))
        sectPr.append(pgNumType)

        # Xóa khung viền thừa kế từ Section 1
        no_borders = parse_xml(r'''
            <w:pgBorders %s>
                <w:top w:val="none"/>
                <w:left w:val="none"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:pgBorders>
        ''' % nsdecls('w'))
        sectPr.append(no_borders)

        # Thiết lập Header căn giữa chứa trường PAGE
        hdr = s2.header
        p_hdr = hdr.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = p_hdr.add_run()
        run.font.name = FONT_FAMILY

        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        p_hdr._p.append(fldSimple)

        return s2

    @classmethod
    def add_body_section(cls, doc: Document):
        """
        Tạo Section 3: Nội dung chính
        - Kế thừa và tiếp tục dãy số trang từ Section 2 đến hết tài liệu
        """
        s3 = doc.add_section(WD_SECTION.NEW_PAGE)
        cls.apply_page_margins(s3)
        s3.header.is_linked_to_previous = True
        s3.footer.is_linked_to_previous = False

        # Không reset số trang, tiếp tục chuỗi đánh số từ Section 2
        sectPr = s3._sectPr
        for child in list(sectPr):
            if child.tag.endswith('pgNumType') or child.tag.endswith('pgBorders'):
                sectPr.remove(child)

        # Đảm bảo không có khung viền
        no_borders = parse_xml(r'''
            <w:pgBorders %s>
                <w:top w:val="none"/>
                <w:left w:val="none"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:pgBorders>
        ''' % nsdecls('w'))
        sectPr.append(no_borders)

        return s3
