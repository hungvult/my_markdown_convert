---
# Cấu hình Metadata đồ án / báo cáo bài tập lớn linh động
# 1. Cơ quan / Đơn vị (tùy biến nhiều dòng trên cùng)
don_vi:
  - "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI"
  - "KHOA CÔNG NGHỆ THÔNG TIN"

# 2. Logo
logo_path: "assets/logo.jpg"

# 3. Loại báo cáo / tài liệu
loai: "BÁO CÁO BÀI TẬP LỚN"

# 4. Nhãn và Tên đề tài (tách thành 2 dòng theo yêu cầu)
nhan_de_tai: "ĐỀ TÀI:"
de_tai:
  - "XÂY DỰNG HỆ THỐNG QUẢN LÝ"
  - "DOANH NGHIỆP TRỰC TUYẾN"

# 5. Bảng thông tin linh động (dạng danh sách cặp nhãn - giá trị)
thong_tin:
  - nhan: "Giảng viên hướng dẫn:"
    gia_tri:
      - "TS. Nguyễn Văn A"
      - "ThS. Trần Văn B"

  - nhan: "Nhóm:"
    gia_tri: "Nhóm 01"

  - nhan: "Lớp:"
    gia_tri: "Công nghệ thông tin 2 - K64"

  - nhan: "Sinh viên thực hiện:"
    gia_tri:
      - "Trần Văn B - 20123456"
      - "Lê Thị C - 20123457"
      - "Phạm Văn D - 20123458"
      - "Hoàng Quốc E - 20123459"
      - "Đặng Thị F - 20123460"

# 6. Địa danh và thời gian
dia_diem: "Hà Nội"
nam: "2026"
---

<!--

================================================================================
                    HƯỚNG DẪN QUY CHUẨN SOẠN THẢO CHO AI VÀ NGƯỜI VIẾT
================================================================================
Tệp này là tài liệu mẫu (Template) chuẩn hóa theo Quy chế Đồ án Tốt nghiệp:
1. Toàn bộ các khối comment HTML sẽ tự động được lọc bỏ khi xuất file .docx.
   Người viết và AI có thể tự do viết ghi chú, prompt, nhắc nhở trong comment.
2. Quy định số thứ tự phân cấp:
   - # TIÊU ĐỀ: Heading 1 (Chương). Tự động sang trang mới, font 18pt Bold căn giữa.
   - ## Tiêu đề mục: Heading 2. Tự động đánh số X.Y (Ví dụ: 1.1), font 16pt Bold lề trái.
   - ### Tiêu đề tiểu mục: Heading 3. Tự động đánh số X.Y.Z (Ví dụ: 1.1.1), font 14pt Bold lề trái.
3. Quy định Bảng (Table):
   - Tiêu đề đặt TRÊN bảng bằng cú pháp: ': Tên bảng {#tbl:id}'
   - Tự động đánh số: 'Bảng X.Y. Tên bảng'
4. Quy định Hình ảnh (Figure):
   - Cú pháp: '![Tên hình ảnh](path){#fig:id}'
   - Tiêu đề tự động đặt DƯỚI ảnh: 'Hình X.Y. Tên hình ảnh'
5. Tham chiếu chéo (Cross-reference):
   - Dùng '[@fig:id]' hoặc '[Hình @fig:id]' -> render thành 'Hình 1.1'
   - Dùng '[@tbl:id]' hoặc '[Bảng @tbl:id]' -> render thành 'Bảng 1.1'
   - Dùng '[@eq:id]' -> render thành '(1.1)'
================================================================================

-->

<!-- SECTION 2: FRONT MATTER -->

# LỜI CẢM ƠN {.frontmatter}

<!-- Hướng dẫn: Viết ngắn gọn tri ân thầy cô hướng dẫn, bộ môn, gia đình và bạn bè -->

Lời cảm ơn ...

# MỤC LỤC {#toc .frontmatter}

<!-- Hướng dẫn: Khối này sẽ tự động nhúng mã trường TOC tự động của Word -->

# DANH MỤC CÁC TỪ VIẾT TẮT {.frontmatter}

<!-- Hướng dẫn: Bảng liệt kê các từ viết tắt trong đồ án -->

| Ký hiệu | Thuật ngữ tiếng Anh               | Thuật ngữ tiếng Việt         |
| :------ | :-------------------------------- | :--------------------------- |
| API     | Application Programming Interface | Giao diện lập trình ứng dụng |

# DANH MỤC BẢNG BIỂU {#lot .frontmatter}

<!-- Hướng dẫn: Tool sẽ tự động tổng hợp danh mục bảng biểu từ các bảng đã đánh số -->

# DANH MỤC HÌNH ẢNH {#lof .frontmatter}

<!-- Hướng dẫn: Tool sẽ tự động tổng hợp danh mục hình ảnh từ các hình đã đánh số -->

<!-- SECTION 3: BODY CONTENT (ĐÁNH SỐ TRANG TỪ 1 Ở HEADER CĂN GIỮA) -->

# MỞ ĐẦU {-}

<!-- Hướng dẫn phần Mở đầu: Nêu lý do chọn đề tài, tính cấp thiết, mục tiêu và cấu trúc báo cáo -->

Lời mở đầu ...

# Mẫu các render

<!-- Chương 1 -->

<!-- Hướng dẫn: Mẫu các đoạn văn bản được render theo định dạng mong muốn -->

Văn bản mẫu minh họa định dạng **in đậm**, _in nghiêng_, đoạn mã
`console.log("demo")`, [liên kết web](!) và công thức nội dòng $E = mc^2$. Trích
dẫn tài liệu tham khảo [@utc2026], [@fowler2018].

- Mục danh sách không thứ tự thứ nhất.
- Mục danh sách không thứ tự thứ hai kèm trích dẫn [@bogddt2021].

1. Bước thực hiện có thứ tự 1.
2. Bước thực hiện có thứ tự 2.

: Bảng so sánh thông số cấu hình {#tbl:so_sanh}

| Thành phần       |     Thông số      |       Ghi chú |
| :--------------- | :---------------: | ------------: |
| Máy chủ ứng dụng | 4 Cores, 16GB RAM | Ubuntu Server |
| Cơ sở dữ liệu    |   PostgreSQL 16   |     Cổng 5432 |

: Ma trận kết quả kiểm nghiệm hiệu năng {#tbl:ma_tran}

<table>
  <thead>
    <tr>
      <th rowspan="2">STT</th>
      <th rowspan="2">Chỉ số</th>
      <th colspan="2">Môi trường</th>
    </tr>
    <tr>
      <th>Nội bộ</th>
      <th>Đám mây</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Độ trễ API</td>
      <td>12ms</td>
      <td>45ms</td>
    </tr>
  </tbody>
</table>

![Sơ đồ kiến trúc tổng quan](assets/architecture.drawio.png){#fig:kientruc}

$$
H(s) = -\sum_{i=1}^{n} p_i \log_2(p_i) \tag{eq:entropy}
$$

Minh họa tham chiếu chéo tự động: đối chiếu dữ liệu tại [@tbl:so_sanh], kết quả
đo lường tại [@tbl:ma_tran], kiến trúc tại [@fig:kientruc] và công thức tính
toán [@eq:entropy].

# PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

<!-- Chương 2 -->

## Yêu cầu chức năng

## Thiết kế kiến trúc tổng quan

## Thiết kế cơ sở dữ liệu

# CÀI ĐẶT VÀ ĐÁNH GIÁ THỰC NGHIỆM

<!-- Chương 3 -->

## Môi trường cài đặt

## Đánh giá hiệu năng và bảo mật

# KẾT LUẬN VÀ KIẾN NGHỊ {-}

## Các kết quả đạt được {-}

## Hướng phát triển tiếp theo {-}

# TÀI LIỆU THAM KHẢO {#references -}

<!-- Hướng dẫn: Không cần điền danh sách thủ công tại đây.
Toàn bộ danh mục tài liệu tham khảo sẽ được tự động trích xuất và định dạng từ tệp references.bib
dựa theo thứ tự các khóa trích dẫn [@citekey] xuất hiện trong bài viết. -->

# PHỤ LỤC A: CẤU HÌNH VÀ DỮ LIỆU BỔ TRỢ {.appendix}

## Danh mục tham số môi trường

## Sơ đồ triển khai chi tiết
