# Bước 0 – Chốt phạm vi

## Quyết định đã có (điền ngày, người xác nhận)
| Hạng mục | Quyết định | Căn cứ |
|---|---|---|
| Gọi API chính thức có được tính là "cào"? | Được, giảng viên đã xác nhận | Email/tin nhắn ngày ___ (đính kèm ảnh chụp vào docs/evidence/) |
| Khu vực | Các trục đường chính đi qua Quận Bình Thạnh, TP.HCM | Họp ngày ___; đổi cách mô tả theo docs/decisions.md D1 |
| Nguồn A | OpenStreetMap (OSMnx) | |
| Nguồn B | TomTom Traffic Flow Segment Data API | |
| Số nguồn / số mẫu tối đa | 2 nguồn / 10.000 mẫu | Đề bài |
| Định dạng lưu | CSV | Đề bài |
| Hạn mức TomTom | 20.000 request/tháng (Freemium) | Ảnh dashboard MyTomTom 10/10/2026 |
| Phương án thu | N đoạn TomTom (12–25, chốt ở Bước 2) x 32 lượt/ngày x 7 ngày; tối đa 5.600 mẫu | Họp ngày ___ |
| Ngày bắt đầu thu 7 ngày | ___/___/2026 (phải gồm cả thứ Bảy và Chủ nhật) | |

## Phân việc Bước 0
| Người | Việc | Đầu ra | Xong |
|---|---|---|---|
| 1 | Xin giảng viên xác nhận bằng văn bản: API chính thức, định dạng nộp, có được công bố bộ dữ liệu không | docs/evidence/lecturer_confirmation.* | ☐ |
| 2 | Lưu ảnh dashboard, đọc điều khoản TomTom (lưu trữ và chia sẻ dữ liệu) và giấy phép OSM (ODbL) | docs/licenses.md | ☐ |
| 3 | Rà soát ngân sách mẫu và config.py | config.py chạy không lỗi | ☐ |
| 4–8 | Đọc docs/schema.md, ghi ít nhất 1 góp ý hoặc "không góp ý" vào Pull Request | PR có comment | ☐ |

## Họp chốt (30 phút) – chương trình
1. Người 3 trình bày ngân sách mẫu (5 phút)
2. Người 2 báo kết quả điều khoản và hạn mức (5 phút)
3. Điểm danh góp ý schema, sửa tại chỗ (15 phút)
4. Chốt ngày bắt đầu thu; ký duyệt schema v1.0 (5 phút)

## Cổng kiểm tra Bước 0
- [ ] Có văn bản xác nhận của giảng viên
- [ ] licenses.md đã điền
- [ ] Schema v1.0 đủ 8 chữ ký
- [ ] Ngày bắt đầu thu đã chốt
