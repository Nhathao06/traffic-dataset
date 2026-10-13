# Bước 1 – Chuẩn bị môi trường (cả 8 người)

## A. Người 1 (làm trước, ~30 phút)
1. Tạo repo GitHub riêng tư, giải nén bộ khung, push lên `main`.
2. Mời 7 người còn lại (quyền Write).
3. Settings → Branches: bảo vệ `main` (bắt buộc Pull Request, 1 người duyệt).
4. Tạo thư mục docs/evidence/ để chứa ảnh chụp dashboard và xác nhận của giảng viên.

## B. Mỗi người
1. Cài Python >= 3.10 và Git. Kiểm tra: `python --version`, `git --version`.
2. Clone repo, tạo môi trường ảo, `pip install -r requirements.txt`.
   - Lỗi cài osmnx/geopandas trên Windows: dùng conda (`conda install -c conda-forge osmnx`) hoặc báo nhóm.
3. Đăng ký tài khoản tại developer.tomtom.com bằng email riêng, vào Keys → tạo API key, đảm bảo key dùng được Traffic API.
4. `cp .env.example .env` rồi dán key. Không gửi key qua chat, không commit.
5. Chạy `python scripts/hello_tomtom.py` -> phải thấy `HTTP status: 200` và tốc độ.
6. Chạy `python scripts/hello_osm.py` -> phải thấy số cạnh và loại đường ở Bình Thạnh.
7. Mở MyTomTom → Analytics → API Usage & Performance → "Show all usage", kiểm tra dòng **Traffic Flow Segment Data API** tăng từ 0 lên >= 1 (có thể trễ vài phút). Dòng này, không phải dòng khác, là dòng bị trừ hạn mức.
8. Tạo nhánh `feature/<ten>-setup`, điền tên vào docs/team.md, mở Pull Request.
9. Tích hàng của mình trong docs/setup_checklist.md.

## C. Riêng người 4
Tạo thêm key "production" cho đợt thu chính. Chỉ người 4 và người 1 giữ. Mọi người khác chỉ test bằng key cá nhân, mỗi người chỉ cần vài chục request.

## D. Lỗi thường gặp
| Hiện tượng | Nguyên nhân / cách xử lý |
|---|---|
| HTTP 403 | Sai key hoặc key chưa bật Traffic API |
| HTTP 429 | Gọi quá nhanh (QPS) hoặc hết hạn mức; chờ rồi thử lại |
| Dashboard vẫn 0 sau 15 phút | Kiểm tra bạn xem đúng dòng Traffic Flow Segment Data; báo trưởng nhóm nếu script trả 200 |
| hello_osm chậm / timeout | Thử lại; giảm AREA_RADIUS_M trong scripts/config.py (báo trưởng nhóm) |
| `ModuleNotFoundError: config` | Chạy từ thư mục gốc repo: `python scripts/hello_osm.py` |

## E. Cổng sang Bước 2
8/8 hàng trong docs/setup_checklist.md đã tích đủ và Bước 0 đã đạt cổng kiểm tra.
