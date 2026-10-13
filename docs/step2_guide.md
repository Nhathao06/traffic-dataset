# Bước 2 – Chọn đoạn đường (cả 8 người, ~1,5 ngày)

Mục tiêu: có file `data/processed/osm_segments.csv` gồm 12–25 đoạn TomTom khác nhau, đã được 8 người kiểm tra.

## Luồng
2a (người 1) -> 2b (người 2) -> 2c + 2d (người 3) -> kiểm tra (cả 8) -> họp chốt -> chạy lại 2c nếu loại đoạn

| Pha | Người | Việc | Đầu ra | Tốn request |
|---|---|---|---|---|
| A | 1 | `python scripts/step2a_osm_candidates.py`, mở file kiểm tra, mở Pull Request | data/processed/osm_candidates.csv (~60 dòng) | 0 |
| B | 2 | Gộp PR của người 1, chạy `python scripts/step2b_probe_candidates.py` | data/processed/candidates_probed.csv + data/raw/probe/*.json | ~60 (key cá nhân của người 2) |
| C | 3 | Gộp PR của người 2, chạy `step2c_select.py` rồi `step2d_map.py` | osm_segments.csv, selection_report.csv, segment_owners.csv, docs/map_selected.html | 0 |
| D | 1–8 | Mỗi người kiểm tra các đoạn của mình (xem segment_owners.csv) | docs/review/review_personN.csv | 0 |
| E | cả nhóm | Họp 30 phút chốt; người 3 chạy lại 2c với --exclude nếu có đoạn bị loại | osm_segments.csv cuối | 0 |

Tại sao một người chạy: tránh 8 người cùng tốn request và cho ra 8 phiên bản khác nhau.

## Pha A – người 1
1. `git pull`, mở cửa sổ lệnh tại thư mục dự án, bật `(.venv)`.
2. `python scripts/step2a_osm_candidates.py` (có thể chờ vài phút).
3. Đạt khi in "Đã ghi ~60 ứng viên" và "Số tên đường khác nhau" >= 20.
4. Mở `data/processed/osm_candidates.csv` bằng Excel, xem có tên đường lạ không.
5. Nhánh `feature/an-candidates`, commit file CSV, mở PR. Báo nhóm.
Lỗi thường gặp: ít hơn 60 ứng viên -> báo leader nới MAX_PER_STREET trong config.py.

## Pha B – người 2
1. Pull bản đã gộp, chạy `python scripts/step2b_probe_candidates.py`.
2. Mỗi dòng in: mã, tên đường, độ dài đoạn TomTom, tỷ lệ trong khung, confidence.
3. Nếu có dòng LỖI: chạy lại đúng lệnh đó, script chỉ gọi lại những cái lỗi.
4. Commit `candidates_probed.csv` và thư mục `data/raw/probe/`, mở PR.

## Pha C – người 3
1. `python scripts/step2c_select.py`
2. Đọc phần tóm tắt: số đoạn được chọn, lý do loại (đếm), phân chia người kiểm tra.
3. Nếu chọn < 12 đoạn: script báo CẢNH BÁO. Báo leader; nới MIN_INSIDE_RATIO (ví dụ 0.4 -> 0.3) hoặc MAX_API_SEG_LENGTH_M, ghi vào docs/decisions.md, chạy lại.
4. `python scripts/step2d_map.py` -> mở `docs/map_selected.html`.
5. Commit các file kết quả + map, mở PR.

## Pha D – cả 8 người (30–45 phút)
1. Mở `data/processed/segment_owners.csv`, tìm các đoạn có `owner` = số của bạn.
2. Mở `docs/map_selected.html` bằng trình duyệt. Xanh lá = được chọn, cam = dự phòng, xám = loại. Bấm vào chấm để xem thông tin.
3. Với từng đoạn của bạn trả lời 4 câu:
   - (1) Đường xanh trên bản đồ có đi qua con đường mang tên `street_name` không?
   - (2) Đoạn có hợp lý không (không chạy ngoằn ngoèo ra khu khác, không quá phần lớn nằm ngoài Bình Thạnh)?
   - (3) Tốc độ có hợp lý không (thường `current_speed` không vượt quá ~1,3 lần `free_flow_speed`)?
   - (4) Mở OpenStreetMap hoặc Google Maps xác nhận tên đường và vị trí.
4. Tạo file `docs/review/review_personN.csv` (N là số của bạn):
```
segment_id,street_name,q1_ten_duong_dung,q2_doan_hop_ly,q3_toc_do_hop_ly,verdict,ghi_chu
S004,Dien Bien Phu,Y,Y,Y,OK,
S005,Nguyen Huu Canh,Y,N,Y,THAY,doan chay ra ngoai Thu Duc
```
`verdict` chỉ ghi `OK` hoặc `THAY`. Mỗi người một file riêng nên không xung đột khi gộp.
5. Mở PR.

## Pha E – họp chốt (30 phút)
1. Leader gom các đoạn `THAY`. Bàn từng cái, loại nếu đa số đồng ý.
2. Người 3 chạy lại: `python scripts/step2c_select.py --exclude C012,C033` (mã `candidate_id` nằm trong cột `candidate_id` của osm_segments.csv). Đoạn dự phòng tự vào thay.
3. Chạy lại `step2d_map.py`, commit.
4. Cập nhật docs/team.md theo segment_owners.csv mới.
5. Chốt số đoạn cuối, cập nhật `N_SEGMENTS` nếu muốn, ghi vào docs/decisions.md.

## Cổng sang Bước 3
- [ ] osm_segments.csv có 12–25 dòng, `api_seg_id` không trùng
- [ ] 8/8 file review đã nộp, mọi đoạn `THAY` đã xử lý
- [ ] map_selected.html mở được, nhóm đã xem
- [ ] decisions.md ghi đủ thay đổi
- [ ] Schema rev.2 đủ 8 chữ ký

## Điều leader cần biết
- Không cần hiểu code. Chỉ cần: mỗi pha có một người chịu trách nhiệm, đầu ra là file cụ thể, "xong" kiểm tra được bằng cách mở file.
- Số đoạn ít hơn 25 là bình thường, không phải thất bại.
- Hạn mức: toàn bộ Bước 2 tốn khoảng 60 request.
