# CÀI ĐẶT VÀ THỰC NGHIỆM

<!-- Hướng dẫn Chương 3: Môi trường triển khai, giao diện, kết quả kiểm thử -->

## Môi trường cài đặt hệ thống

Hệ thống được đóng gói bằng công nghệ container hóa (Docker) giúp việc triển khai đồng nhất trên mọi môi trường máy chủ.

## Đánh giá hiệu năng và an toàn

$$ E = \sum_{i=1}^{m} w_i \cdot x_i $$ {#eq:weight_sum}

Công thức [@eq:weight_sum] được áp dụng để tính điểm đánh giá an toàn tài nguyên.

## Đánh giá ma trận kiểm thử

Kết quả kiểm thử hiệu năng chi tiết được trình bày trong [@tbl:eval_matrix].

: Bảng ma trận kết quả kiểm thử đa môi trường {#tbl:eval_matrix}
<table>
  <thead>
    <tr>
      <th rowspan="2">STT</th>
      <th rowspan="2">Chỉ số đánh giá</th>
      <th colspan="2">Kết quả đo lường</th>
      <th rowspan="2">Trạng thái</th>
    </tr>
    <tr>
      <th>Môi trường Thử nghiệm</th>
      <th>Môi trường Vận hành</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Thời gian phản hồi API (ms)</td>
      <td>120</td>
      <td>45</td>
      <td>Đạt chuẩn</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Tải CPU tối đa (%)</td>
      <td>65%</td>
      <td>38%</td>
      <td>Tối ưu</td>
    </tr>
  </tbody>
</table>
