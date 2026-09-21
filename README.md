# md2docx: Bộ biên dịch Markdown sang DOCX chuẩn Đồ án Tốt nghiệp

Công cụ tự động hóa quá trình chuyển đổi tài liệu từ Markdown sang định dạng
Microsoft Word (.docx), tuân thủ 100% quy chuẩn trình bày Báo cáo Đồ án Tốt
nghiệp (ĐATN) của Trường Đại học Giao thông Vận tải.

Hệ thống được thiết kế phục vụ quy trình cộng tác viết tài liệu giữa người dùng
và Trí tuệ Nhân tạo (AI), hỗ trợ tính toán tĩnh (static resolution) số hiệu phân
cấp và loại bỏ toàn bộ comment chỉ dẫn khi xuất bản.

---

## 1. Cấu trúc thư mục

```
doc/
├── .venv/                      # Môi trường ảo Python độc lập (PEP 668 compliant)
├── md2docx/                    # Mã nguồn công cụ lõi
│   ├── config.py               # Cấu hình lề A4, font Times New Roman, khoảng cách đoạn
│   ├── parser.py               # AST Parser & bộ lọc comment HTML đa tầng
│   ├── indexer.py              # Bộ đánh số phân cấp tĩnh 2-pass và resolve tham chiếu chéo
│   ├── cover_generator.py      # Bộ sinh Trang bìa & Phụ bìa chuẩn Phụ lục 1 (khung viền đôi)
│   ├── section_manager.py      # Quản lý 3 Section OOXML (Bìa, Front Matter, Body có Header số trang)
│   ├── docx_builder.py         # Trình dựng tài liệu DOCX, bảng biểu, hình ảnh, công thức
│   └── cli.py                  # Giao diện dòng lệnh CLI
├── chapters/                   # Mẫu viết phân chia theo chương (00_... đến 06_...)
├── assets/                     # Tài nguyên ảnh, sơ đồ và logo trường
│   └── logo.jpg                # Logo
├── thesis.yaml                 # Cấu hình thông tin bìa đồ án
├── template.md                 # Tệp mẫu đơn tích hợp đầy đủ chỉ dẫn trong comment HTML
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── build.sh                    # Script biên dịch một lệnh
└── README.md                   # Tài liệu hướng dẫn sử dụng
```

---

## 2. Cài đặt và Môi trường

Hệ thống sử dụng Python 3.10+ với môi trường ảo riêng biệt:

```bash
# Tự động tạo venv và cài dependencies khi chạy build.sh lần đầu
./build.sh template.md
```

Hoặc cài đặt thủ công:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

---

## 3. Hướng dẫn sử dụng

### 3.1. Cấu hình thông tin Đồ án (`thesis.yaml`)

Chỉnh sửa thông tin sinh viên, giảng viên và đề tài tại tệp `thesis.yaml`:

```yaml
truong: "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI"
khoa: "KHOA CÔNG NGHỆ THÔNG TIN"
de_tai: "TÊN ĐỀ TÀI CỦA ĐỒ ÁN TỐT NGHIỆP"
gvhd: "TS. Nguyễn Văn A"
svth: "Trần Văn B"
mssv: "20123456"
lop: "Công nghệ thông tin 2 - K64"
nam: "2026"
logo_path: "assets/logo.jpg"
```

### 3.2. Lệnh biên dịch

#### Chế độ 1: Tệp đơn lẻ (`template.md`)

Phù hợp khi toàn bộ nội dung được viết trong một tệp duy nhất:

```bash
./build.sh template.md Bao_Cao_Tot_Nghiep.docx thesis.yaml
```

#### Chế độ 2: Thư mục phân chia theo chương (`chapters/`)

Khuyến nghị sử dụng khi làm việc với AI để tránh tràn token ngữ cảnh:

```bash
./build.sh chapters Bao_Cao_Tot_Nghiep.docx thesis.yaml
```

Trình biên dịch sẽ tự động quét và hợp nhất các tệp `.md` trong thư mục theo thứ
tự bảng chữ cái của tên tệp (`00_...`, `01_...`, `02_...`).

---

## 4. Quy ước cú pháp Markdown (Dành cho Người viết & AI)

### 4.1. Tiêu đề phân cấp (Headings)

- `# TÊN TIÊU ĐỀ`: Heading 1. Tự động ngắt trang, căn giữa, in đậm 18pt.
  - Các tiêu đề Front Matter (`LỜI CẢM ƠN`, `LỜI CAM ĐOAN`, `MỤC LỤC`,
    `DANH MỤC...`) nằm ở Section 2.
  - Các tiêu đề Chương tự động được gán tiền tố `CHƯƠNG X.` và chuyển sang
    Section 3.
- `## Tên mục`: Heading 2. Tự động đánh số `X.Y.` (ví dụ: `1.1.`), căn trái, in
  đậm 16pt.
- `### Tên tiểu mục`: Heading 3. Tự động đánh số `X.Y.Z.` (ví dụ: `1.1.1.`), căn
  trái, in đậm 14pt.

### 4.2. Hình ảnh (Figures)

Cú pháp đặt trong văn bản:

```markdown
![Sơ đồ kiến trúc tổng quan của hệ thống](assets/architecture.png){#fig:arch}
```

- Ảnh được căn giữa trang, tự động giới hạn độ rộng vừa lề giấy.
- Tiêu đề tự động đặt **PHÍA DƯỚI** ảnh theo định dạng:
  `Hình X.Y. Sơ đồ kiến trúc tổng quan của hệ thống`.

### 4.3. Bảng biểu (Tables)

Cú pháp đặt nhãn chú thích ngay trước bảng:

```markdown
: Bảng thông tin tài khoản người dùng {#tbl:users} | Tên trường | Kiểu dữ liệu |
Mô tả | | :--- | :--- | :--- | | id | BIGINT | Khóa chính | | username |
VARCHAR(50) | Tên đăng nhập |
```

- Tiêu đề tự động đặt **PHÍA TRÊN** bảng theo định dạng:
  `Bảng X.Y. Bảng thông tin tài khoản người dùng`.
- Các bảng không gắn chú thích (như Bảng danh mục từ viết tắt) sẽ không bị đánh
  số thứ tự.

### 4.4. Công thức toán học (Equations)

```markdown
$$ H(s) = -\sum\_{i=1}^{n} p_i \log_2(p_i) $$ {#eq:entropy}
```

- Công thức căn giữa trang.
- Nhãn số phương trình dạng `(X.Y)` tự động đặt sát lề phải.

### 4.5. Tham chiếu chéo (Cross-references)

Trong nội dung đoạn văn, sử dụng cú pháp:

- `[@fig:arch]` hoặc `[Hình @fig:arch]` → Biên dịch thành `Hình 2.1`
- `[@tbl:users]` hoặc `[Bảng @tbl:users]` → Biên dịch thành `Bảng 2.1`
- `[@eq:entropy]` → Biên dịch thành `(3.1)`

### 4.6. Trích dẫn tài liệu tham khảo (BibTeX & Vancouver)

Tích hợp trực tiếp với cơ sở dữ liệu `references.bib` và extension **VS Code Markdown Notes**:
- **Cấu hình VS Code** (`.vscode/settings.json`):
  ```json
  {
    "vscodeMarkdownNotes.bibtexFilePath": "doc/references.bib"
  }
  ```
- **Cú pháp trích dẫn trong bài**:
  - Trích dẫn đơn: `[@fowler2018]` hoặc `@fowler2018` → Biên dịch thành `[1]`
  - Trích dẫn nhiều tài liệu: `[@fowler2018; @bogddt2021]` hoặc `[@fowler2018], [@bogddt2021]` → Tự động chuẩn hóa và sắp xếp tăng dần không khoảng trắng: `[1],[2]`
- **Tự động sinh danh mục**:
  Tại mục `# TÀI LIỆU THAM KHẢO`, tool tự động kết xuất danh sách theo đúng thứ tự xuất hiện trong bài viết và chuẩn hóa theo quy chế ĐATN.

### 4.7. Chú thích tài liệu và Prompt cho AI (HTML Comments)

Toàn bộ nội dung đặt trong các thẻ comment HTML:

```markdown
<!--
Hướng dẫn cho AI:
Viết chi tiết mục 2.2 về thiết kế kiến trúc theo chuẩn microservices...
-->
```

Toàn bộ khối comment này sẽ được bộ lọc loại bỏ hoàn toàn, không xuất hiện trong bản in DOCX/PDF cuối cùng.

---

## 5. Quy chuẩn kỹ thuật được áp dụng

| Thành phần             | Quy định                                                         | Hiện thực hóa kỹ thuật                                                    |
| :--------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Khổ giấy & Lề**      | A4; Trên: 2.5cm, Dưới: 2.5cm, Trái: 3.0cm, Phải: 2.0cm           | Thiết lập đơn vị dxa: Top/Bottom 1417, Left 1701, Right 1134              |
| **Số trang**           | Căn giữa, **phía trên đầu trang**                                | Header (Top Center): Thẻ OOXML `<w:fldSimple w:instr="PAGE"/>`            |
| **Khởi tạo số trang**  | Bắt đầu từ 1 tại phần Mở đầu / Chương 1                          | Section 3 cấu hình `<w:pgNumType w:start="1"/>`                           |
| **Trang bìa**          | Mẫu Phụ lục 1 có khung viền đôi                                  | Section 1 áp dụng `<w:pgBorders w:val="double"/>`, không có Header/Footer |
| **Đoạn văn (Body)**    | Times New Roman 13pt, căn đều hai bên, dãn dòng 1.2, thụt lề 1cm | `w:jc="both"`, `w:line="288"`, `w:firstLine="567"`                        |
| **Mục lục & Danh mục** | Tự động cập nhật                                                 | Nhúng trường Word `TOC` và tự động sinh bảng danh mục Hình/Bảng tĩnh      |
