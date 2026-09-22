# PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

<!-- Hướng dẫn Chương 2: Phân tích ca sử dụng (Use case), kiến trúc phần mềm, thiết kế CSDL -->

## Phân tích yêu cầu chức năng

Hệ thống cung cấp các chức năng chính:
- Đăng ký, đăng nhập và phân quyền người dùng (RBAC).
- Quản lý dữ liệu tập trung và thống kê thời gian thực.

## Thiết kế kiến trúc tổng quan

![Sơ đồ kiến trúc tổng quan của đồ án](assets/logo.jpg){#fig:arch_chapter2}

Hình ảnh [@fig:arch_chapter2] minh họa luồng xử lý giữa các tầng trong ứng dụng.

## Thiết kế cơ sở dữ liệu

: Bảng lưu trữ vai trò người dùng (roles) {#tbl:roles}
| Mã vai trò | Tên vai trò | Mô tả quyền hạn |
| :--- | :--- | :--- |
| ADMIN | Quản trị viên | Toàn quyền hệ thống |
| MANAGER | Quản lý bộ phận | Phê duyệt và báo cáo |
| USER | Nhân viên | Thao tác tác vụ cơ bản |

Bảng phân quyền tại [@tbl:roles] đảm bảo nguyên tắc đặc quyền tối thiểu (least privilege).
