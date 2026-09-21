"""
Cấu hình quy chuẩn định dạng Báo cáo Đồ án Tốt nghiệp
Căn cứ: Quy định trình bày đồ án tốt nghiệp - Trường ĐH Giao thông Vận tải
"""
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# 1. Khổ giấy & Lề (A4)
PAGE_WIDTH = Cm(21.0)
PAGE_HEIGHT = Cm(29.7)
MARGIN_TOP = Cm(2.5)      # 1417 dxa
MARGIN_BOTTOM = Cm(2.5)   # 1417 dxa
MARGIN_LEFT = Cm(3.0)     # 1701 dxa
MARGIN_RIGHT = Cm(2.0)    # 1134 dxa

# Đơn vị dxa cho OOXML
DXA_MARGIN_TOP = 1417
DXA_MARGIN_BOTTOM = 1417
DXA_MARGIN_LEFT = 1701
DXA_MARGIN_RIGHT = 1134

# 2. Font chữ & Màu
FONT_FAMILY = "Times New Roman"
COLOR_BLACK = RGBColor(0, 0, 0)

# 3. Đoạn văn nội dung (Body Text)
BODY_FONT_SIZE = Pt(13)
BODY_LINE_SPACING = 1.2           # Dãn dòng 1.2 lines
BODY_FIRST_LINE_INDENT = Cm(1.0)  # Thụt đầu dòng 1cm (~567 dxa)
BODY_ALIGNMENT = WD_ALIGN_PARAGRAPH.JUSTIFY
BODY_SPACE_AFTER = Pt(3)
BODY_SPACE_BEFORE = Pt(0)

# 4. Tiêu đề Chương (Heading 1)
H1_FONT_SIZE = Pt(18)
H1_BOLD = True
H1_ALIGNMENT = WD_ALIGN_PARAGRAPH.CENTER
H1_SPACE_BEFORE = Pt(0)
H1_SPACE_AFTER = Pt(12)

# 5. Tiêu đề Mục (Heading 2)
H2_FONT_SIZE = Pt(16)
H2_BOLD = True
H2_ALIGNMENT = WD_ALIGN_PARAGRAPH.LEFT
H2_SPACE_BEFORE = Pt(6)
H2_SPACE_AFTER = Pt(6)

# 6. Tiêu đề Tiểu mục (Heading 3)
H3_FONT_SIZE = Pt(14)
H3_BOLD = True
H3_ALIGNMENT = WD_ALIGN_PARAGRAPH.LEFT
H3_SPACE_BEFORE = Pt(6)
H3_SPACE_AFTER = Pt(6)

# 7. Chú thích Bảng và Hình ảnh (Captions)
CAPTION_FONT_SIZE = Pt(12)
CAPTION_FONT_STYLE = "Times New Roman"
CAPTION_ALIGNMENT = WD_ALIGN_PARAGRAPH.CENTER
CAPTION_SPACE_BEFORE = Pt(4)
CAPTION_SPACE_AFTER = Pt(4)

# 8. Bảng biểu (Table formatting)
TABLE_ALIGNMENT = WD_TABLE_ALIGNMENT.CENTER
TABLE_HEADER_BG = "E8EEF5"  # Xanh nhạt chuyên nghiệp
TABLE_BORDER_COLOR = "CCCCCC"
