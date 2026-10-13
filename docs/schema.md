# Hợp đồng dữ liệu (schema) – v1.0 rev.2 (CHỜ KÝ DUYỆT)

> Cả 8 người ký ở cuối file. Sau khi ký, muốn đổi phải qua trưởng nhóm và ghi vào "Lịch sử thay đổi".

## Quy ước chung
- Phạm vi: các trục đường chính đi qua Quận Bình Thạnh, TP.HCM
- **Đơn vị phân tích = một đoạn TomTom** (một trục đường có thể dài vài km). OSM bổ sung thuộc tính (tên, loại đường, số làn, giới hạn tốc độ). Xem docs/decisions.md, quyết định D1.
- Múi giờ UTC+7. Thời gian: `YYYY-MM-DD HH:MM:SS`
- UTF-8, phân cách dấu phẩy, dòng đầu là tên cột, snake_case
- Tốc độ km/h; thời gian di chuyển giây; độ dài mét
- Giá trị thiếu: để trống (không ghi "NA", "null", "-1")
- `segment_id`: `S001`…, số đoạn do Bước 2 quyết định (tối đa 25, tối thiểu 12)

## Ngân sách mẫu
- N đoạn x 32 lượt/ngày (06:00–21:30, mỗi 30 phút) x 7 ngày. Với N = 25: 5.600 mẫu; N = 15: 3.360 mẫu. Luôn <= 10.000.
- Collector tự dừng ở 9.500 dòng raw
- Hạn mức TomTom (Traffic Flow Segment Data API): 20.000 request/tháng

## 1) osm_segments.csv  (danh mục đoạn, được tạo ở Bước 2)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| segment_id | str | khóa chính |
| candidate_id | str | mã ứng viên ở Bước 2 (truy vết) |
| osm_way_id | str | id way trong OSM |
| street_name | str | |
| highway_type | str | trunk/primary/secondary |
| lanes | int | có thể thiếu, KHÔNG tự điền ở Bước 2 |
| maxspeed_kmh | int | có thể thiếu, KHÔNG tự điền ở Bước 2 |
| oneway | bool | |
| length_m | int | độ dài cạnh OSM (khác độ dài đoạn TomTom) |
| lat, lon | float | điểm dùng để hỏi API (trung điểm cạnh OSM) |
| api_seg_id | str | mã đoạn TomTom kỳ vọng (băm điểm đầu + điểm cuối) |
| api_seg_length_m | int | độ dài đoạn TomTom |
| api_seg_inside_ratio | float | tỷ lệ chiều dài đoạn TomTom nằm trong khung Bình Thạnh (0–1) |

## 2) traffic_raw.csv  (Nguồn B, thô, append-only, không sửa tay)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| segment_id | str | |
| collected_at | datetime | thời điểm gọi API (UTC+7) |
| current_speed | float | km/h |
| free_flow_speed | float | km/h |
| current_travel_time | int | giây |
| free_flow_travel_time | int | giây |
| confidence | float | 0–1 |
| road_closure | bool | |
| api_seg_id | str | mã đoạn TomTom thực tế trả về lần này (so với danh mục để phát hiện đổi đoạn) |
| api_seg_length_m | int | |
| api_start_lat, api_start_lon | float | điểm đầu đoạn TomTom trả về |
| api_end_lat, api_end_lon | float | điểm cuối đoạn |
| http_status | int | 200 = OK; dòng lỗi vẫn được ghi |

## 3) traffic_integrated.csv  (sản phẩm cuối)
segment_id, street_name, highway_type, lanes, maxspeed_kmh, length_m, lat, lon,
api_seg_id, api_seg_length_m, api_seg_inside_ratio, seg_changed,
timestamp, day_of_week, hour, is_weekend, is_peak_hour,
current_speed, free_flow_speed, travel_time_s, congestion_index, congestion_level,
confidence, is_imputed, lanes_imputed, maxspeed_imputed, match_suspect

- `seg_changed` = 1 nếu `api_seg_id` của dòng khác `api_seg_id` trong danh mục (TomTom đổi cách chia đoạn).
- `match_suspect` thay vai trò kiểm tra map-matching: gắn cờ khi `api_seg_inside_ratio` thấp hoặc `seg_changed` = 1.

## Công thức dẫn xuất
- congestion_index = current_speed / free_flow_speed
- congestion_level: > 0.8 "thong_thoang"; 0.5–0.8 "dong"; < 0.5 "un_tac"
- is_peak_hour: 06:30–09:00 và 16:30–19:00 (ngưỡng tham khảo)

## Lịch sử thay đổi
| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| v0.1 | 10/10/2026 | Bản nháp |
| v1.0 | 10/10/2026 | Chốt Bình Thạnh, hạn mức 20.000/tháng |
| v1.0 rev.2 | 11/10/2026 | Sau khi thử API: đoạn TomTom dài 2,5–25 km. Đơn vị phân tích đổi thành đoạn TomTom; thêm các cột api_seg_id, api_seg_length_m, api_seg_inside_ratio, api_end_*, seg_changed; số đoạn 12–25 |

## Chữ ký duyệt (ghi "Đồng ý" + ngày)
| # | Họ tên | Ký |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
