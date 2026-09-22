# PHỤ LỤC A: CẤU HÌNH VÀ DỮ LIỆU BỔ TRỢ {.appendix}

## Danh mục tham số môi trường

Chi tiết các tham số môi trường được thống kê trong [@tbl:app_env].

: Bảng các biến môi trường triển khai {#tbl:app_env}
| Biến môi trường | Giá trị mặc định | Giải thích |
| :--- | :--- | :--- |
| APP_ENV | production | Môi trường triển khai ứng dụng |
| DB_PORT | 5432 | Cổng kết nối cơ sở dữ liệu |
| CACHE_TTL | 3600 | Thời gian sống của bản ghi cache (giây) |

## Sơ đồ cấu trúc chi tiết

![Sơ đồ kiến trúc module mở rộng](assets/logo.jpg){#fig:app_diagram}

Sơ đồ tại [@fig:app_diagram] thể hiện các thành phần mở rộng trong phụ lục.

### Hàm mục tiêu tối ưu hóa

Hàm mục tiêu được biểu diễn theo công thức:

$$ J(w, b) = \frac{1}{m} \sum_{i=1}^m L(\hat{y}^{(i)}, y^{(i)}) $$ {#eq:app_loss}

Công thức tối ưu hóa [@eq:app_loss] được sử dụng trong quá trình huấn luyện mô hình.
