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
Lời đầu tiên, em xin gửi lời cảm ơn chân thành và sâu sắc nhất tới thầy/cô hướng dẫn đã tận tình chỉ bảo, định hướng khoa học và động viên em trong suốt quá trình nghiên cứu và hoàn thành đồ án tốt nghiệp này.

Em cũng xin gửi lời cảm ơn chân thành tới các thầy cô giáo trong Khoa Công nghệ thông tin - Trường Đại học Giao thông Vận tải đã truyền thụ những kiến thức nền tảng quý báu trong những năm học vừa qua.

# LỜI CAM ĐOAN {.frontmatter}

<!-- Hướng dẫn: Cam kết đồ án tự nghiên cứu, không sao chép trái phép -->
Em xin cam đoan đồ án tốt nghiệp với đề tài **"Xây dựng hệ thống quản lý doanh nghiệp trực tuyến"** là công trình nghiên cứu do chính em thực hiện dưới sự hướng dẫn khoa học của thầy/cô hướng dẫn. Các kết quả, số liệu và tài liệu trích dẫn trong đồ án đều trung thực và có nguồn gốc rõ ràng.

# MỤC LỤC {#toc .frontmatter}

<!-- Hướng dẫn: Khối này sẽ tự động nhúng mã trường TOC tự động của Word -->

# DANH MỤC CÁC TỪ VIẾT TẮT {.frontmatter}

<!-- Hướng dẫn: Bảng liệt kê các từ viết tắt trong đồ án -->

| Ký hiệu | Thuật ngữ tiếng Anh | Thuật ngữ tiếng Việt |
| :--- | :--- | :--- |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| DBMS | Database Management System | Hệ quản trị cơ sở dữ liệu |
| ĐATN | | Đồ án tốt nghiệp |
| REST | Representational State Transfer | Phong cách kiến trúc mạng |
| UI/UX | User Interface / User Experience | Giao diện / Trải nghiệm người dùng |

# DANH MỤC BẢNG BIỂU {#lot .frontmatter}

<!-- Hướng dẫn: Tool sẽ tự động tổng hợp danh mục bảng biểu từ các bảng đã đánh số -->

# DANH MỤC HÌNH ẢNH {#lof .frontmatter}

<!-- Hướng dẫn: Tool sẽ tự động tổng hợp danh mục hình ảnh từ các hình đã đánh số -->

<!-- SECTION 3: BODY CONTENT (ĐÁNH SỐ TRANG TỪ 1 Ở HEADER CĂN GIỮA) -->

# MỞ ĐẦU {-}

<!-- Hướng dẫn phần Mở đầu: Nêu lý do chọn đề tài, tính cấp thiết, mục tiêu và cấu trúc báo cáo -->
Trong bối cảnh chuyển đổi số mạnh mẽ của cuộc cách mạng công nghiệp 4.0, các doanh nghiệp ngày càng chú trọng việc ứng dụng công nghệ thông tin vào công tác quản trị và điều hành sản xuất kinh doanh. Việc xây dựng một hệ thống quản lý tích hợp, linh hoạt và bảo mật cao là nhu cầu cấp thiết nhằm tối ưu hóa chi phí vận hành và nâng cao năng lực cạnh tranh.

Đồ án này tập trung nghiên cứu và xây dựng giải pháp hệ thống quản trị nguồn lực doanh nghiệp trực tuyến dựa trên nền tảng đám mây và kiến trúc dịch vụ hiện đại.

# TỔNG QUAN VỀ HỆ THỐNG QUẢN LÝ DOANH NGHIỆP

<!-- Hướng dẫn: Chương 1 tổng quan về lý thuyết, hiện trạng bài toán -->

## Bối cảnh và tính cấp thiết

Quản trị doanh nghiệp truyền thống bằng sổ sách hoặc các phần mềm rời rạc thường gây ra tình trạng phân mảnh thông tin, khó khăn trong việc báo cáo số liệu thời gian thực và tiềm ẩn nhiều sai sót trong quản lý tồn kho và tài chính. Theo quy định đào tạo đại học [@bogddt2021], việc thực hiện đồ án tốt nghiệp đòi hỏi sinh viên giải quyết bài toán thực tế dựa trên các chuẩn mực kiến trúc chuyên nghiệp [@fowler2018].

## Khảo sát hiện trạng các giải pháp tương tự

Hiện nay trên thị trường đã có một số giải pháp thương mại và mã nguồn mở phục vụ quản lý doanh nghiệp. Tuy nhiên, các giải pháp này thường có chi phí triển khai cao hoặc chưa tối ưu hóa cho quy trình đặc thù của doanh nghiệp vừa và nhỏ tại Việt Nam.

## Ghi chú kỹ thuật {-}

Phần này là ví dụ về tiêu đề không đánh số thứ tự (Unnumbered Heading) sử dụng cú pháp `{-}` hoặc `{.unnumbered}`. Mục này vẫn xuất hiện đầy đủ trong Mục lục (TOC) nhưng không mang tiền tố số phân cấp.

## Mục tiêu và phạm vi nghiên cứu

Việc trình bày báo cáo tuân thủ hướng dẫn của Khoa CNTT [@utc2026] kết hợp đối chiếu các nguyên lý thiết kế [@fowler2018], [@bogddt2021].

: So sánh ưu nhược điểm của các giải pháp quản lý {#tbl:so_sanh}
| Giải pháp | Chi phí | Khả năng tùy biến | Độ phức tạp triển khai |
| :--- | :--- | :--- | :--- |
| Sổ sách / Excel | Thấp | Thủ công, dễ lỗi | Đơn giản |
| Odoo Open Source | Trung bình | Tốt, cần chuyên gia | Trung bình |
| SAP ERP | Rất cao | Phức tạp | Rất phức tạp |
| **Hệ thống đề xuất** | **Hợp lý** | **Cao, linh hoạt** | **Nhanh chóng** |

Dựa trên bảng so sánh tại [@tbl:so_sanh], việc nghiên cứu một hệ thống tùy biến cao, giao diện trực quan và chi phí vận hành tối ưu là hoàn toàn phù hợp với thực tiễn.

# PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

<!-- Hướng dẫn: Chương 2 phân tích ca sử dụng (Use case), kiến trúc hệ thống và CSDL -->

## Yêu cầu chức năng

Hệ thống cung cấp các nhóm chức năng chính:
- Phân hệ quản lý người dùng và xác thực tập trung.
- Phân hệ quản lý danh mục sản phẩm, kho vận.
- Phân hệ quản lý đơn hàng và báo cáo thống kê trực quan.

## Thiết kế kiến trúc tổng quan

Hệ thống được thiết kế theo mô hình 3 lớp (3-tier architecture) kết hợp dịch vụ RESTful API độc lập giữa Frontend và Backend.

![Sơ đồ kiến trúc tổng quan của hệ thống](assets/logo.jpg){#fig:kientruc}

Như được mô tả trực quan tại [@fig:kientruc], thành phần Client giao tiếp với Application Server thông qua giao thức HTTPS bảo mật.

## Thiết kế cơ sở dữ liệu

: Bảng thông tin tài khoản người dùng (users) {#tbl:users}
| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Định danh người dùng |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Tên đăng nhập |
| email | VARCHAR(100) | UNIQUE, NOT NULL | Địa chỉ thư điện tử |
| role | VARCHAR(20) | DEFAULT 'STAFF' | Vai trò phân quyền |
| created_at | TIMESTAMP | CURRENT_TIMESTAMP | Thời điểm tạo |

Cấu trúc bảng tại [@tbl:users] được tối ưu hóa cho các thao tác truy vấn và chỉ mục (indexing).

# CÀI ĐẶT VÀ ĐÁNH GIÁ THỰC NGHIỆM

<!-- Hướng dẫn: Chương 3 trình bày việc triển khai mã nguồn, kiểm thử hiệu năng -->

## Môi trường cài đặt

Hệ thống được kiểm thử trên môi trường Linux Server với cấu hình: CPU 4 cores, RAM 8GB, SSD 160GB.

## Đánh giá hiệu năng và bảo mật

Hệ thống áp dụng thuật toán mã hóa mật khẩu và tính toán độ phức tạp theo công thức:

$$
H(s) = -\sum_{i=1}^{n} p_i \log_2(p_i)
$$ {#eq:entropy}

Công thức tính toán [@eq:entropy] cho phép định lượng mức độ ngẫu nhiên của chuỗi bảo mật được cấp phát cho người dùng.

# KẾT LUẬN VÀ KIẾN NGHỊ {-}

## Các kết quả đạt được {-}

Đồ án đã hoàn thành các mục tiêu đặt ra:
1. Nghiên cứu tổng quan cơ sở lý thuyết và khảo sát nhu cầu quản lý thực tế.
2. Thiết kế chi tiết kiến trúc, mô hình CSDL và giao diện người dùng.
3. Hiện thực hóa hệ thống và triển khai kiểm thử đạt yêu cầu.

## Hướng phát triển tiếp theo {-}

- Nghiên cứu tích hợp trí tuệ nhân tạo (AI) để dự báo nhu cầu thị trường và tối ưu hóa tồn kho tự động.
- Phát triển ứng dụng trên nền tảng di động (iOS / Android).

# TÀI LIỆU THAM KHẢO {#references -}

<!-- Hướng dẫn: Không cần điền danh sách thủ công tại đây.
Toàn bộ danh mục tài liệu tham khảo sẽ được tự động trích xuất và định dạng từ tệp references.bib
dựa theo thứ tự các khóa trích dẫn [@citekey] xuất hiện trong bài viết. -->

# PHỤ LỤC A: CẤU HÌNH VÀ DỮ LIỆU BỔ TRỢ {.appendix}

## Danh mục tham số môi trường

Chi tiết các tham số môi trường được thống kê trong [@tbl:env_params].

: Bảng các biến môi trường triển khai {#tbl:env_params}
| Biến môi trường | Giá trị mặc định | Giải thích |
| :--- | :--- | :--- |
| APP_ENV | production | Môi trường triển khai ứng dụng |
| DB_PORT | 5432 | Cổng kết nối cơ sở dữ liệu |
| CACHE_TTL | 3600 | Thời gian sống của bản ghi cache (giây) |

## Sơ đồ triển khai chi tiết

![Kiến trúc phụ trợ và luồng dữ liệu](assets/logo.jpg){#fig:app_module}

Mô hình triển khai chi tiết được thể hiện trong [@fig:app_module].

### Hàm mục tiêu tối ưu hóa

Hàm mục tiêu được biểu diễn theo công thức:

$$
J(w, b) = \frac{1}{m} \sum_{i=1}^m L(\hat{y}^{(i)}, y^{(i)})
$$ {#eq:loss}

Công thức tối ưu hóa [@eq:loss] được sử dụng trong quá trình huấn luyện mô hình.
