"""
Bộ phân tích cú pháp Markdown và HTML (Parser)
- Loại bỏ toàn bộ comment HTML (<!-- ... -->)
- Trích xuất Frontmatter YAML
- Nhận diện cú pháp đặc biệt: caption bảng (: ...), ảnh ({#fig:...}), công thức ($$...$$)
"""
import re
import yaml
from markdown_it import MarkdownIt

class MarkdownDocParser:
    def __init__(self):
        # Cấu hình markdown-it hỗ trợ table, strikethrough, HTML
        self.md = MarkdownIt("commonmark", {"breaks": False, "html": True})
        self.md.enable("table")
        self.md.enable("strikethrough")

    @staticmethod
    def strip_comments(text: str) -> str:
        """Loại bỏ hoàn toàn các khối comment HTML <!-- ... -->, hỗ trợ cả comment lồng nhau"""
        result = []
        i = 0
        n = len(text)
        while i < n:
            if text[i:i+4] == '<!--':
                depth = 1
                i += 4
                while i < n and depth > 0:
                    if text[i:i+4] == '<!--':
                        depth += 1
                        i += 4
                    elif text[i:i+3] == '-->':
                        depth -= 1
                        i += 3
                    else:
                        i += 1
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)

    @staticmethod
    def extract_frontmatter(text: str) -> tuple[dict, str]:
        """Trích xuất YAML Frontmatter ở đầu file nếu có"""
        metadata = {}
        cleaned_text = text.lstrip()
        if cleaned_text.startswith("---"):
            parts = cleaned_text.split("---", 2)
            if len(parts) >= 3:
                raw_yaml = parts[1]
                try:
                    metadata = yaml.safe_load(raw_yaml) or {}
                except Exception as e:
                    print(f"[CẢNH BÁO] Lỗi khi đọc Frontmatter YAML: {e}")
                content = parts[2]
                return metadata, content
        return metadata, text

    @staticmethod
    def clean_inline_breaks(text: str) -> str:
        """
        Chuẩn hóa xuống dòng trong văn bản Markdown inline theo chuẩn CommonMark:
        - Hard break (2+ dấu cách cuối dòng, backslash \\ cuối dòng, hoặc thẻ <br>): Bảo toàn thành '\n'
        - Soft break (dấu enter đơn lẻ trong mã nguồn Markdown): Chuyển thành 1 khoảng trắng ' '
        """
        if not text:
            return ""
        # 1. Bảo toàn hardbreak thành marker tạm
        text = re.sub(r'(?:[ \t]{2,}|\\)\r?\n[ \t]*', '__HARDBREAK__', text)
        text = re.sub(r'<br\s*/?>', '__HARDBREAK__', text, flags=re.IGNORECASE)
        # 2. Xóa bỏ softbreak (dấu xuống dòng đơn) và thu gọn khoảng trắng xung quanh
        text = re.sub(r'[ \t]*\r?\n[ \t]*', ' ', text)
        # 3. Khôi phục hardbreak thành '\n'
        return text.replace('__HARDBREAK__', '\n')

    def parse_to_tokens(self, text: str):
        """
        Tiền xử lý văn bản và sinh danh sách tokens của markdown-it
        """
        # 1. Bỏ comment
        clean_text = self.strip_comments(text)
        
        # 2. Chuẩn hóa caption bảng đặt trước bảng:
        # Cú pháp: ': Tên bảng {#tbl:id}' hoặc 'Table: Tên bảng {#tbl:id}'
        # Chuyển đổi thành marker để dễ nhận diện trong AST
        clean_text = re.sub(
            r'^[ \t]*(?::|Table:)[ \t]*(.+?)(?:\{#(tbl:[\w-]+)\})?[ \t]*$',
            r'<!--TABLE_CAPTION: \1 | \2-->',
            clean_text,
            flags=re.MULTILINE
        )
        
        # 3. Chuẩn hóa khối công thức toán $$ ... $$ {#eq:id}
        def math_block_repl(m):
            eq_content = m.group(1).strip()
            eq_id = m.group(2) if m.group(2) else ""
            return f"\n\n<!--MATH_BLOCK: {eq_content} | {eq_id}-->\n\n"

        clean_text = re.sub(
            r'\$\$\s*\n?(.*?)\n?\s*\$\$(?:[ \t]*\n?[ \t]*\{#(eq:[\w-]+)\})?',
            math_block_repl,
            clean_text,
            flags=re.DOTALL
        )

        tokens = self.md.parse(clean_text)
        return tokens
