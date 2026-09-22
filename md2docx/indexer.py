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
        
        # Chế độ phụ lục (Appendix Mode)
        self.in_appendix = False
        self.appendix_idx = 0
        self.current_appendix_letter = ""
        
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
        
        # Document structural auditing flags
        self.has_toc_heading = False
        self.has_lof_heading = False
        self.has_lot_heading = False
        self.has_references_heading = False

    def _parse_heading_attributes(self, raw_title: str) -> tuple[str, bool, Optional[str], set]:
        """
        Bóc tách các thuộc tính như {-}, {.unnumbered}, {.appendix}, {.frontmatter}, {#id} từ tiêu đề Markdown.
        Trả về: (clean_title, is_unnumbered, heading_id, classes)
        """
        is_unnumbered = False
        heading_id = None
        classes = set()
        
        m = re.search(r'\s*\{([^}]+)\}\s*$', raw_title)
        if m:
            raw_attr = m.group(1).strip()
            tokens = raw_attr.split()
            recognized = False
            for tok in tokens:
                if tok == '-' or tok.lower() in ('.unnumbered', 'unnumbered'):
                    is_unnumbered = True
                    recognized = True
                elif tok.startswith('.'):
                    classes.add(tok[1:].lower())
                    recognized = True
                elif tok.startswith('#'):
                    heading_id = tok[1:].lower()
                    recognized = True
                elif tok.lower() in ('appendix', 'frontmatter', 'toc', 'lof', 'lot', 'references', 'bibliography'):
                    classes.add(tok.lower())
                    recognized = True
            
            if recognized:
                clean = raw_title[:m.start()].strip()
                return clean, is_unnumbered, heading_id, classes

        return raw_title.strip(), is_unnumbered, heading_id, classes

    def lint_heading(self, level: int, clean_title: str, info: dict):
        """Kiểm tra và cảnh báo nếu tiêu đề nghi vấn chức năng nhưng thiếu thuộc tính bắt buộc"""
        if level != 1:
            return
            
        t_upper = clean_title.upper()
        
        if ("MỤC LỤC" in t_upper or "TABLE OF CONTENTS" in t_upper) and not info.get("is_toc"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' có khả năng là Mục lục nhưng thiếu '{{#toc .frontmatter}}'. Bảng Mục lục tự động sẽ không được sinh ra!")
            
        elif ("DANH MỤC HÌNH" in t_upper or "DANH MỤC CÁC HÌNH" in t_upper or "LIST OF FIGURES" in t_upper) and not info.get("is_lof"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' có khả năng là Danh mục hình ảnh nhưng thiếu '{{#lof .frontmatter}}'. Danh mục hình sẽ không được sinh ra!")
            
        elif ("DANH MỤC BẢNG" in t_upper or "DANH MỤC CÁC BẢNG" in t_upper or "LIST OF TABLES" in t_upper) and not info.get("is_lot"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' có khả năng là Danh mục bảng biểu nhưng thiếu '{{#lot .frontmatter}}'. Danh mục bảng sẽ không được sinh ra!")
            
        elif ("TÀI LIỆU THAM KHẢO" in t_upper or "REFERENCES" in t_upper or "BIBLIOGRAPHY" in t_upper) and not info.get("is_references"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' có khả năng là Tài liệu tham khảo nhưng thiếu '{{#references -}}'. Danh mục trích dẫn BibTeX sẽ không được kết xuất!")
            
        elif re.match(r'^(?:PHỤ\s+LỤC|APPENDIX)\b', t_upper) and not info.get("is_appendix"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' có khả năng là Phụ lục nhưng thiếu '{{.appendix}}'. Các đề mục con và bảng/hình sẽ không chuyển sang đánh số chữ cái (A, B, C...)!")
            
        elif any(fm in t_upper for fm in ["LỜI CẢM ƠN", "LỜI CAM ĐOAN", "TÓM TẮT"]) and not info.get("is_front_matter"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' thuộc phần đầu tài liệu nhưng thiếu '{{.frontmatter}}'. Tiêu đề này sẽ bị xử lý như một Chương nội dung!")
            
        elif any(sb in t_upper for sb in ["MỞ ĐẦU", "KẾT LUẬN"]) and not info.get("is_unnumbered"):
            print(f"[CẢNH BÁO] Tiêu đề '{clean_title}' thường là phần không đánh số nhưng thiếu '{{-}}'. Tiêu đề này sẽ được đánh số như một Chương bình thường!")

    def audit_document(self):
        """Kiểm toán tổng thể tài liệu sau Pass 1 và in cảnh báo nếu thiếu các thành phần cấu trúc"""
        warnings = []
        if not self.has_toc_heading:
            warnings.append("[CẢNH BÁO] Tài liệu không chứa tiêu đề Mục lục '{#toc .frontmatter}'. Báo cáo xuất ra sẽ thiếu bảng Mục lục.")
        if self.figures_catalog and not self.has_lof_heading:
            warnings.append(f"[CẢNH BÁO] Tài liệu có chứa {len(self.figures_catalog)} hình ảnh nhưng thiếu tiêu đề Danh mục hình '{{#lof .frontmatter}}'.")
        if self.tables_catalog and not self.has_lot_heading:
            warnings.append(f"[CẢNH BÁO] Tài liệu có chứa {len(self.tables_catalog)} bảng biểu nhưng thiếu tiêu đề Danh mục bảng '{{#lot .frontmatter}}'.")
        if self.cited_entries and not self.has_references_heading:
            warnings.append(f"[CẢNH BÁO] Tài liệu trích dẫn {len(self.cited_entries)} nguồn tài liệu BibTeX nhưng không có tiêu đề '{{#references -}}'. Danh mục trích dẫn sẽ không xuất hiện.")
        
        for w in warnings:
            print(w)

    def register_heading(self, level: int, raw_title: str) -> dict:
        """
        Đăng ký tiêu đề và phân loại 100% qua thuộc tính tường minh
        """
        raw_title = raw_title.strip()
        clean_title, is_unnumbered, heading_id, classes = self._parse_heading_attributes(raw_title)
        
        # Nhận diện cờ chức năng từ thuộc tính
        is_toc = heading_id == 'toc' or 'toc' in classes
        is_lof = heading_id in ('lof', 'figures') or 'lof' in classes or 'figures' in classes
        is_lot = heading_id in ('lot', 'tables') or 'lot' in classes or 'tables' in classes
        is_references = heading_id in ('references', 'bibliography') or 'references' in classes or 'bib' in classes
        is_appendix = 'appendix' in classes or heading_id == 'appendix'
        is_front_matter = 'frontmatter' in classes or is_toc or is_lof or is_lot

        if is_toc:
            self.has_toc_heading = True
        if is_lof:
            self.has_lof_heading = True
        if is_lot:
            self.has_lot_heading = True
        if is_references:
            self.has_references_heading = True

        # Heading 1
        if level == 1:
            if is_front_matter:
                self.in_appendix = False
                res = {
                    "level": 1,
                    "type": "front_matter",
                    "display": clean_title.upper(),
                    "chapter_num": 0,
                    "is_front_matter": True,
                    "is_toc": is_toc,
                    "is_lof": is_lof,
                    "is_lot": is_lot,
                    "is_references": False,
                    "is_appendix": False,
                    "is_unnumbered": True,
                    "id": heading_id
                }
            elif is_appendix:
                self.in_appendix = True
                # Trích xuất ký tự chữ cái nếu có trong tiêu đề (ví dụ: Phụ lục A, Phụ lục B)
                m_letter = re.search(r'(?:PHỤ\s+LỤC|APPENDIX)\s+([A-Za-z]|\d+)', clean_title, re.IGNORECASE)
                if m_letter:
                    spec = m_letter.group(1)
                    if spec.isalpha():
                        letter = spec.upper()
                        self.appendix_idx = ord(letter) - ord('A') + 1
                    else:
                        self.appendix_idx = int(spec)
                        letter = chr(ord('A') + self.appendix_idx - 1)
                else:
                    self.appendix_idx += 1
                    letter = chr(ord('A') + self.appendix_idx - 1)

                self.current_appendix_letter = letter
                self.h2_idx = 0
                self.h3_idx = 0
                self.fig_idx = 0
                self.tbl_idx = 0
                self.eq_idx = 0

                # Chuẩn hóa tên hiển thị phụ lục
                if not re.match(r'^(?:PHỤ\s+LỤC|APPENDIX)\b', clean_title, re.IGNORECASE):
                    display = f"PHỤ LỤC {letter}. {clean_title.upper()}"
                else:
                    display = clean_title.upper()

                res = {
                    "level": 1,
                    "type": "special_body",
                    "display": display,
                    "chapter_num": self.chapter_idx,
                    "appendix_letter": letter,
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": True,
                    "is_unnumbered": is_unnumbered,
                    "id": heading_id
                }
            elif is_references:
                self.in_appendix = False
                res = {
                    "level": 1,
                    "type": "special_body",
                    "display": clean_title.upper(),
                    "chapter_num": self.chapter_idx,
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": True,
                    "is_appendix": False,
                    "is_unnumbered": True,
                    "id": heading_id
                }
            elif is_unnumbered:
                self.in_appendix = False
                m = re.match(r'^(?:CHƯƠNG\s+\d+[\.:\s]*|\d+[\.:\s]*)(.*)$', clean_title, re.IGNORECASE)
                final_title = m.group(1).strip() if m else clean_title
                res = {
                    "level": 1,
                    "type": "special_body",
                    "display": final_title.upper(),
                    "chapter_num": self.chapter_idx,
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": False,
                    "is_unnumbered": True,
                    "id": heading_id
                }
            else:
                # Chương thông thường
                self.in_appendix = False
                self.chapter_idx += 1
                self.h2_idx = 0
                self.h3_idx = 0
                self.fig_idx = 0
                self.tbl_idx = 0
                self.eq_idx = 0
                
                m = re.match(r'^(?:CHƯƠNG\s+\d+[\.:\s]*)(.*)$', clean_title, re.IGNORECASE)
                c_title = m.group(1).strip() if m else clean_title
                display = f"CHƯƠNG {self.chapter_idx}. {c_title.upper()}"
                res = {
                    "level": 1,
                    "type": "chapter",
                    "display": display,
                    "chapter_num": self.chapter_idx,
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": False,
                    "is_unnumbered": False,
                    "id": heading_id
                }

        # Heading 2
        elif level == 2:
            if is_unnumbered:
                c_title = re.sub(r'^(?:(?:[A-Za-z]|\d+)(?:\.\d+)+)[\.:\s]+', '', clean_title).strip()
                res = {
                    "level": 2,
                    "type": "section",
                    "display": c_title,
                    "num": "",
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": self.in_appendix,
                    "is_unnumbered": True,
                    "id": heading_id
                }
            else:
                self.h2_idx += 1
                self.h3_idx = 0
                curr_prefix = self.current_appendix_letter if self.in_appendix else str(max(1, self.chapter_idx))
                c_title = re.sub(r'^(?:(?:[A-Za-z]|\d+)\.\d+)[\.:\s]+', '', clean_title).strip()
                display = f"{curr_prefix}.{self.h2_idx}. {c_title}"
                res = {
                    "level": 2,
                    "type": "section",
                    "display": display,
                    "num": f"{curr_prefix}.{self.h2_idx}",
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": self.in_appendix,
                    "is_unnumbered": False,
                    "id": heading_id
                }

        # Heading 3
        elif level == 3:
            if is_unnumbered:
                c_title = re.sub(r'^(?:(?:[A-Za-z]|\d+)(?:\.\d+)+)[\.:\s]+', '', clean_title).strip()
                res = {
                    "level": 3,
                    "type": "subsection",
                    "display": c_title,
                    "num": "",
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": self.in_appendix,
                    "is_unnumbered": True,
                    "id": heading_id
                }
            else:
                self.h3_idx += 1
                curr_prefix = self.current_appendix_letter if self.in_appendix else str(max(1, self.chapter_idx))
                curr_h2 = max(1, self.h2_idx)
                c_title = re.sub(r'^(?:(?:[A-Za-z]|\d+)\.\d+\.\d+)[\.:\s]+', '', clean_title).strip()
                display = f"{curr_prefix}.{curr_h2}.{self.h3_idx}. {c_title}"
                res = {
                    "level": 3,
                    "type": "subsection",
                    "display": display,
                    "num": f"{curr_prefix}.{curr_h2}.{self.h3_idx}",
                    "is_front_matter": False,
                    "is_toc": False,
                    "is_lof": False,
                    "is_lot": False,
                    "is_references": False,
                    "is_appendix": self.in_appendix,
                    "is_unnumbered": False,
                    "id": heading_id
                }

        else:
            res = {"level": level, "type": "heading", "display": clean_title, "id": heading_id}

        if heading_id:
            self.symbols[heading_id] = res.get("display", clean_title)
            if not heading_id.startswith("sec:"):
                self.symbols[f"sec:{heading_id}"] = res.get("display", clean_title)

        # Chạy bộ linter cảnh báo tiêu đề
        self.lint_heading(level, clean_title, res)

        return res

    def register_figure(self, caption: str, fig_id: Optional[str] = None) -> tuple[str, str]:
        """
        Đánh số hình ảnh theo chương / phụ lục: Hình <Chương/Phụ_lục>.<Thứ_tự>
        """
        self.fig_idx += 1
        curr_prefix = self.current_appendix_letter if self.in_appendix else str(max(1, self.chapter_idx))
        label_num = f"{curr_prefix}.{self.fig_idx}"
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
        Đánh số bảng biểu theo chương / phụ lục: Bảng <Chương/Phụ_lục>.<Thứ_tự>
        """
        self.tbl_idx += 1
        curr_prefix = self.current_appendix_letter if self.in_appendix else str(max(1, self.chapter_idx))
        label_num = f"{curr_prefix}.{self.tbl_idx}"
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
        Đánh số phương trình: (<Chương/Phụ_lục>.<Thứ_tự>)
        """
        self.eq_idx += 1
        curr_prefix = self.current_appendix_letter if self.in_appendix else str(max(1, self.chapter_idx))
        label = f"({curr_prefix}.{self.eq_idx})"
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
