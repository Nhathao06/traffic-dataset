# Nhật ký quyết định

## D1 – Đơn vị phân tích là "đoạn TomTom" (11/10/2026)
**Phát hiện:** thử API tại ngã tư Hàng Xanh cho đoạn dài 9.589 m; đổi zoom 10→18 không đổi kết quả. Quét lưới 12 điểm trong khung Bình Thạnh ra 9 đoạn khác nhau, dài 2,6–25,6 km, nhiều đoạn chạy ra ngoài quận; có điểm khác nhau trả về cùng một đoạn.
**Quyết định:**
1. Mỗi "đoạn" của bộ dữ liệu là một đoạn TomTom, nhận diện bằng `api_seg_id`.
2. Chọn đoạn bằng cách probe ~60 điểm ứng viên OSM (~60 request) rồi lọc: confidence >= 0.6, đoạn <= 10 km, >= 40% chiều dài nằm trong khung, không trùng đoạn.
3. Số đoạn 12–25 (tối đa theo đề, không cần đủ 25).
4. Phạm vi mô tả: "các trục đường chính đi qua Quận Bình Thạnh".
5. Thêm các cột api_seg_* để mọi dòng dữ liệu cho biết nó đại diện cho đoạn dài bao nhiêu.
**Lý do:** giữ được tính trung thực của dữ liệu và biến sự chênh lệch độ phân giải giữa hai nguồn thành điểm phân tích trong phần tích hợp.
**Hạn chế phải ghi trong báo cáo:** tốc độ là trung bình của cả đoạn dài; đoạn có thể mang tính một chiều; TomTom có thể đổi cách chia đoạn theo thời gian.
**Ngưỡng:** MIN_INSIDE_RATIO, MAX_API_SEG_LENGTH_M, MIN_CONFIDENCE trong scripts/config.py; nới nếu chọn được dưới 12 đoạn (ghi lý do vào file này).
