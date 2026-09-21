"""
Bộ định chỉ mục và tính toán tĩnh 2-pass (Indexer & Static Resolver)
- Pass 1: Quét AST, gán số thứ tự phân cấp cho Chương, Mục, Tiểu mục, Bảng, Hình, Phương trình.
- Pass 2: Thay thế tham chiếu chéo ([@fig:...], [@tbl:...], [@eq:...]) thành số hiển thị tĩnh.
"""
import re
from typing import Dict, List, Any, Optional

class DocIndexer:
    def __init__(self):
        # State counters
        self.chapter_idx = 0
        self.h2_idx = 0
        self.h3_idx = 0
        self.fig_idx = 0
        self.tbl_idx = 0
        self.eq_idx = 0
        
        # Symbol table: id -> display_label (ví dụ: 'fig:arch' -> 'Hình 1.1')
        self.symbols: Dict[str, str] = {}
        
        # Danh mục để xuất bảng tra cứu
        self.figures_catalog: List[Dict[str, Any]] = []
        self.tables_catalog: List[Dict[str, Any]] = []
        
        # Cơ sở dữ liệu và bộ theo dõi trích dẫn BibTeX (Vancouver)
        self.bib_entries: Dict[str, dict] = {}
        self.citation_counter = 0
        self.citation_map: Dict[str, int] = {}
        self.cited_entries: List[dict] = []
        
        # Danh sách các tiêu đề đặc biệt thuộc Front Matter
        self.front_matter_titles = {
            "LỜI CẢM ƠN", "LỜI CAM ĐOAN", "TÓM TẮT", "MỤC LỤC",
            "DANH MỤC CÁC KÝ HIỆU, CÁC CHỮ VIẾT TẮT",
            "DANH MỤC CÁC TỪ VIẾT TẮT",
            "DANH MỤC BẢNG BIỂU", "DANH MỤC CÁC BẢNG",
            "DANH MỤC HÌNH ẢNH", "DANH MỤC CÁC HÌNH VẼ, ĐỒ THỊ"
        }
        
        # Tiêu đề đặc biệt thuộc Body nhưng không mang số chương (hoặc là chương cuối)
        self.special_body_titles = {
            "MỞ ĐẦU", "KẾT LUẬN VÀ KIẾN NGHỊ", "KẾT LUẬN",
            "DANH MỤC TÀI LIỆU THAM KHẢO", "TÀI LIỆU THAM KHẢO", "PHỤ LỤC"
        }

    def is_front_matter(self, title: str) -> bool:
        t_upper = title.strip().upper()
        return any(fm in t_upper for fm in self.front_matter_titles)

    def is_special_body(self, title: str) -> bool:
        t_upper = title.strip().upper()
        return any(sb in t_upper for sb in self.special_body_titles)

    def register_heading(self, level: int, raw_title: str) -> dict:
        """
        Đăng ký tiêu đề và chuẩn hóa tên theo quy chuẩn ĐATN
        """
        raw_title = raw_title.strip()
        t_upper = raw_title.upper()
        
        # Heading 1
        if level == 1:
            if self.is_front_matter(raw_title):
                return {
                    "level": 1,
                    "type": "front_matter",
                    "display": t_upper,
                    "chapter_num": 0
                }
            elif self.is_special_body(raw_title):
                # Tiêu đề chính không có tiền tố Chương (Mở đầu, Kết luận...)
                return {
                    "level": 1,
                    "type": "special_body",
                    "display": t_upper,
                    "chapter_num": self.chapter_idx
                }
            else:
                # Chương thông thường
                self.chapter_idx += 1
                self.h2_idx = 0
                self.h3_idx = 0
                self.fig_idx = 0
                self.tbl_idx = 0
                self.eq_idx = 0
                
                # Kiểm tra nếu người dùng đã ghi sẵn "CHƯƠNG X..."
                m = re.match(r'^(?:CHƯƠNG\s+\d+[\.:\s]*)(.*)$', raw_title, re.IGNORECASE)
                clean_title = m.group(1).strip() if m else raw_title
                display = f"CHƯƠNG {self.chapter_idx}. {clean_title.upper()}"
                return {
                    "level": 1,
                    "type": "chapter",
                    "display": display,
                    "chapter_num": self.chapter_idx
                }
                
        # Heading 2 (Mục X.Y)
        elif level == 2:
            self.h2_idx += 1
            self.h3_idx = 0
            curr_chap = max(1, self.chapter_idx)
            # Lọc bỏ tiền tố số đã có nếu có
            clean_title = re.sub(r'^\d+\.\d+[\.:\s]*', '', raw_title).strip()
            display = f"{curr_chap}.{self.h2_idx}. {clean_title}"
            return {
                "level": 2,
                "type": "section",
                "display": display,
                "num": f"{curr_chap}.{self.h2_idx}"
            }
            
        # Heading 3 (Tiểu mục X.Y.Z)
        elif level == 3:
            self.h3_idx += 1
            curr_chap = max(1, self.chapter_idx)
            curr_h2 = max(1, self.h2_idx)
            clean_title = re.sub(r'^\d+\.\d+\.\d+[\.:\s]*', '', raw_title).strip()
            display = f"{curr_chap}.{curr_h2}.{self.h3_idx}. {clean_title}"
            return {
                "level": 3,
                "type": "subsection",
                "display": display,
                "num": f"{curr_chap}.{curr_h2}.{self.h3_idx}"
            }
            
        return {"level": level, "type": "heading", "display": raw_title}

    def register_figure(self, caption: str, fig_id: Optional[str] = None) -> tuple[str, str]:
        """
        Đánh số hình ảnh theo chương: Hình <Chương>.<Thứ_tự>
        """
        self.fig_idx += 1
        curr_chap = max(1, self.chapter_idx)
        label_num = f"{curr_chap}.{self.fig_idx}"
        label_text = f"Hình {label_num}"
        full_caption = f"{label_text}. {caption}" if caption else label_text
        
        if fig_id:
            # Lưu vào bảng tra cứu
            clean_id = fig_id.strip()
            self.symbols[clean_id] = label_text
            if not clean_id.startswith("fig:"):
                self.symbols[f"fig:{clean_id}"] = label_text

        self.figures_catalog.append({
            "num": label_num,
            "label": label_text,
            "caption": caption,
            "full_caption": full_caption
        })
        return label_text, full_caption

    def register_table(self, caption: str, tbl_id: Optional[str] = None) -> tuple[str, str]:
        """
        Đánh số bảng biểu theo chương: Bảng <Chương>.<Thứ_tự>
        """
        self.tbl_idx += 1
        curr_chap = max(1, self.chapter_idx)
        label_num = f"{curr_chap}.{self.tbl_idx}"
        label_text = f"Bảng {label_num}"
        full_caption = f"{label_text}. {caption}" if caption else label_text
        
        if tbl_id:
            clean_id = tbl_id.strip()
            self.symbols[clean_id] = label_text
            if not clean_id.startswith("tbl:"):
                self.symbols[f"tbl:{clean_id}"] = label_text

        self.tables_catalog.append({
            "num": label_num,
            "label": label_text,
            "caption": caption,
            "full_caption": full_caption
        })
        return label_text, full_caption

    def register_equation(self, eq_id: Optional[str] = None) -> str:
        """
        Đánh số phương trình: (<Chương>.<Thứ_tự>)
        """
        self.eq_idx += 1
        curr_chap = max(1, self.chapter_idx)
        label = f"({curr_chap}.{self.eq_idx})"
        if eq_id:
            clean_id = eq_id.strip()
            self.symbols[clean_id] = label
            if not clean_id.startswith("eq:"):
                self.symbols[f"eq:{clean_id}"] = label
        return label

    def load_bibtex(self, bib_path: str):
        """Đọc và phân tích cú pháp tệp BibTeX (.bib)"""
        import os
        if not os.path.exists(bib_path):
            return
        
        try:
            with open(bib_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            pattern = r'@(\w+)\s*\{\s*([^,]+),\s*(.*?)\n\s*\}'
            matches = re.finditer(pattern, content, re.DOTALL)
            for m in matches:
                entry_type = m.group(1).lower()
                key = m.group(2).strip()
                fields_str = m.group(3)
                fields = {'_type': entry_type, '_key': key}
                field_pattern = r'(\w+)\s*=\s*[\"{](.*?)[\"}]'
                for f_m in re.finditer(field_pattern, fields_str, re.DOTALL):
                    val = re.sub(r'[{}]', '', f_m.group(2))
                    fields[f_m.group(1).lower()] = re.sub(r'\s+', ' ', val).strip()
                self.bib_entries[key] = fields
        except Exception as e:
            print(f"[CẢNH BÁO] Không đọc được tệp BibTeX {bib_path}: {e}")

    def scan_citations(self, text: str):
        """Pass 1: Quét các khóa trích dẫn trong văn bản để đánh số thứ tự xuất hiện (Vancouver)"""
        # Bắt cú pháp [@key] hoặc [@key1; @key2] hoặc @key
        keys = re.findall(r'@([\w:-]+)', text)
        for k in keys:
            # Loại trừ nếu là tham chiếu hình/bảng/công thức đã biết
            if k.startswith(('fig:', 'tbl:', 'eq:')):
                continue
            if k in self.bib_entries and k not in self.citation_map:
                self.citation_counter += 1
                self.citation_map[k] = self.citation_counter
                self.cited_entries.append(self.bib_entries[k])

    def format_bibliography_entry(self, entry: dict, idx: int) -> str:
        """Định dạng mục tài liệu tham khảo theo quy chuẩn ĐATN"""
        author = entry.get('author', 'Tác giả')
        year = entry.get('year', 'n.d.')
        title = entry.get('title', 'Tên tài liệu')
        e_type = entry.get('_type', 'misc')

        if e_type == 'article':
            journal = entry.get('journal', '')
            vol = entry.get('volume', '')
            num = entry.get('number', '')
            pages = entry.get('pages', '')
            vol_num = f", {vol}({num})" if vol and num else (f", {vol}" if vol else "")
            pages_str = f", {pages}" if pages else ""
            return f"{author} ({year}). {title}. *{journal}*{vol_num}{pages_str}."

        elif e_type == 'book':
            publisher = entry.get('publisher', '')
            address = entry.get('address', '')
            pub_info = f", {publisher}" if publisher else ""
            addr_info = f", {address}" if address else ""
            return f"{author} ({year}). *{title}*{pub_info}{addr_info}."

        elif e_type in ('misc', 'techreport', 'manual'):
            howpublished = entry.get('howpublished', entry.get('publisher', ''))
            address = entry.get('address', '')
            pub_info = f", {howpublished}" if howpublished else ""
            addr_info = f", {address}" if address else ""
            return f"{author} ({year}). *{title}*{pub_info}{addr_info}."

        return f"{author} ({year}). *{title}*."

    def resolve_cross_references(self, text: str) -> str:
        """
        Pass 2: Thay thế [@fig:...], [@tbl:...], [@eq:...] và [@citekey] bằng số hiển thị
        """
        # 1. Thay thế tham chiếu hình ảnh, bảng biểu, công thức
        def replace_ref(match):
            prefix = match.group(1) or ""
            ref_id = match.group(2)
            if ref_id in self.symbols:
                return f"{prefix}{self.symbols[ref_id]}"
            elif f"fig:{ref_id}" in self.symbols:
                return f"{prefix}{self.symbols[f'fig:{ref_id}']}"
            elif f"tbl:{ref_id}" in self.symbols:
                return f"{prefix}{self.symbols[f'tbl:{ref_id}']}"
            elif f"eq:{ref_id}" in self.symbols:
                return f"{prefix}{self.symbols[f'eq:{ref_id}']}"
            elif ref_id in self.citation_map:
                return f"{prefix}[{self.citation_map[ref_id]}]"
            return match.group(0)

        pattern = r'\[(Hình\s+|Bảng\s+|Công thức\s+)?@([\w:-]+)\]'
        text = re.sub(pattern, replace_ref, text)

        # 2. Xử lý trích dẫn nhiều tài liệu: [@k1; @k2] hoặc [@k1, @k2]
        def repl_multi_cite(m):
            raw_keys = m.group(1)
            keys = re.findall(r'@([\w:-]+)', raw_keys)
            resolved = []
            for k in keys:
                if k in self.citation_map:
                    resolved.append(f"[{self.citation_map[k]}]")
                elif k in self.symbols:
                    resolved.append(self.symbols[k])
                else:
                    resolved.append(f"[@{k}]")
            return ",".join(resolved)

        text = re.sub(r'\[(@[\w:-]+(?:\s*[;,]\s*@[\w:-]+)+)\]', repl_multi_cite, text)

        # 3. Chuẩn hóa và sắp xếp tăng dần các trích dẫn liền kề: [2],[1] -> [1],[2] (không khoảng trắng)
        def sort_adjacent_citations(m):
            nums = sorted(list(set(int(x) for x in re.findall(r'\[(\d+)\]', m.group(0)))))
            return ",".join(f"[{n}]" for n in nums)

        text = re.sub(r'\[\d+\](?:\s*,\s*\[\d+\])+', sort_adjacent_citations, text)

        # 4. Standalone citation @key
        def repl_standalone_cite(m):
            k = m.group(1)
            if k in self.citation_map:
                return f"[{self.citation_map[k]}]"
            return m.group(0)

        text = re.sub(r'(?<!\w)@([\w:-]+)', repl_standalone_cite, text)

        return text
