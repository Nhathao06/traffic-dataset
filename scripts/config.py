"""Cấu hình dùng chung cho cả dự án. Muốn đổi giá trị phải báo trưởng nhóm."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

# ---- Phạm vi không gian ----
AREA_NAME = "Các trục đường chính đi qua Quận Bình Thạnh, TP.HCM"
AREA_CENTER = (10.8100, 106.7100)      # (lat, lon) tâm tham chiếu
AREA_RADIUS_M = 3000                   # bán kính tải OSM (m)
# Khung bao xấp xỉ để lọc đoạn đường. KIỂM TRA LẠI trên bản đồ ở Bước 2.
AREA_BBOX = {"south": 10.7900, "north": 10.8420, "west": 106.6850, "east": 106.7400}

# ---- Bước 2a: chọn điểm ứng viên từ OSM ----
HIGHWAY_TYPES = ["trunk", "primary", "secondary"]
N_CANDIDATES = 60
OSM_MIN_EDGE_M = 100                   # bỏ cạnh OSM quá ngắn
MAX_PER_STREET = 3                     # tối đa số điểm ứng viên trên 1 tên đường
MIN_SPACING_M = 700                    # khoảng cách tối thiểu giữa 2 điểm cùng tên đường

# ---- Bước 2c: tiêu chí chọn đoạn TomTom ----
ZOOM = 12                              # zoom không ảnh hưởng kết quả (đã thử 10..18)
N_SEGMENTS = 25                        # tối đa số đoạn chọn
N_SEGMENTS_MIN = 12                    # dưới mức này phải nới tiêu chí
N_BACKUP = 10                          # số đoạn dự phòng
MIN_INSIDE_RATIO = 0.4                 # tỷ lệ chiều dài đoạn TomTom nằm trong khung Bình Thạnh
MAX_API_SEG_LENGTH_M = 10_000          # bỏ đoạn TomTom dài hơn mức này
MIN_CONFIDENCE = 0.6
N_OWNERS = 8

# ---- Thu thập ----
TIMEZONE = "Asia/Ho_Chi_Minh"          # UTC+7
COLLECT_FIRST_HOUR = 6                 # lượt đầu 06:00
COLLECT_LAST_SLOT = "21:30"            # lượt cuối 21:30
INTERVAL_MIN = 30
DAYS = 7
RUNS_PER_DAY = 32                      # 06:00 ... 21:30, mỗi 30 phút
REQUEST_DELAY_S = 0.3                  # nghỉ giữa 2 request (tránh vượt QPS)

# ---- Giới hạn ----
MAX_SAMPLES = 10_000                   # trần của đề bài
HARD_CAP_ROWS = 9_500                  # collector tự dừng ở mức này
MONTHLY_QUOTA = 20_000                 # Traffic Flow Segment Data API (dashboard 10/10/2026)

# Số mẫu tối đa dự kiến (nếu chọn đủ N_SEGMENTS đoạn)
EXPECTED_SAMPLES = N_SEGMENTS * RUNS_PER_DAY * DAYS   # 5.600
assert EXPECTED_SAMPLES <= MAX_SAMPLES, "Vượt trần 10.000 mẫu"
assert EXPECTED_SAMPLES <= HARD_CAP_ROWS
