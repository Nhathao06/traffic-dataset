# Bộ dữ liệu lưu lượng giao thông đa nguồn – Quận Bình Thạnh, TP.HCM

- Nguồn A: OpenStreetMap (OSMnx) – mạng lưới đường
- Nguồn B: TomTom Traffic Flow Segment Data API – tốc độ giao thông
- Giới hạn: tối đa 2 nguồn, tối đa 10.000 mẫu, lưu CSV
- Kế hoạch: N đoạn TomTom (12–25) x 32 lượt/ngày x 7 ngày (tối đa 5.600 mẫu)
- Quyết định thiết kế: xem docs/decisions.md

## Bắt đầu (mỗi thành viên)
Xem docs/step1_setup.md. Tóm tắt:
```bash
git clone <repo-url> && cd traffic-dataset
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env  -> điền key của BẠN
python scripts/hello_tomtom.py
python scripts/hello_osm.py
```
## Quy tắc
- Không push thẳng `main`; nhánh `feature/<ten>-<viec>`, merge qua Pull Request, cần 1 người duyệt.
- Không commit `.env` hoặc API key.
- Không sửa tay file trong `data/raw/`.
- Mọi hằng số dùng chung nằm ở `scripts/config.py`.

## Cấu trúc
Bước 2: docs/step2_guide.md
docs/ (schema, giấy phép, checklist, nhật ký) · scripts/ · data/{raw,processed,mock} · report/ · logs/
