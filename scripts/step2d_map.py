"""Bước 2d: vẽ bản đồ để cả nhóm kiểm tra bằng mắt.
Đầu ra: docs/map_selected.html  (mở bằng trình duyệt)
 - Đường XANH LÁ: đoạn TomTom của ứng viên được chọn; CAM: dự phòng; XÁM: bị loại/trùng
 - Chấm tròn: điểm đã hỏi API. Khung đỏ: khung bao Bình Thạnh (xấp xỉ).
Chạy:  python scripts/step2d_map.py        (KHÔNG tốn request)
"""
import json

import folium
import pandas as pd

import config as C

rep = pd.read_csv(C.DATA_PROC / "selection_report.csv")
seg = pd.read_csv(C.DATA_PROC / "osm_segments.csv")
sid = dict(zip(seg["candidate_id"], seg["segment_id"]))

B = C.AREA_BBOX
m = folium.Map(location=C.AREA_CENTER, zoom_start=13, tiles="OpenStreetMap")
folium.Rectangle([[B["south"], B["west"]], [B["north"], B["east"]]], color="red", weight=2, fill=False,
                 tooltip="Khung bao Bình Thạnh (xấp xỉ)").add_to(m)

COLORS = {"selected": "green", "backup": "orange", "duplicate": "gray", "rejected": "gray"}
WEIGHT = {"selected": 5, "backup": 4, "duplicate": 2, "rejected": 2}
for status in ["rejected", "duplicate", "backup", "selected"]:   # vẽ cái quan trọng sau cùng (nằm trên)
    for r in rep[rep["status"] == status].to_dict("records"):
        f = C.DATA_RAW / "probe" / f"{r['candidate_id']}.json"
        label = sid.get(r["candidate_id"], r["candidate_id"])
        info = (f"<b>{label}</b> ({r['candidate_id']}) – {r['street_name']}<br>Trạng thái: {status}<br>"
                f"{r['reject_reason'] if isinstance(r['reject_reason'], str) else ''}<br>"
                f"Đoạn TomTom: {r['api_seg_length_m']} m, trong khung: {r['api_seg_inside_ratio']}<br>"
                f"Tốc độ {r['current_speed']}/{r['free_flow_speed']} km/h, confidence {r['confidence']}")
        if f.exists():
            pts = json.loads(f.read_text(encoding="utf-8"))["coordinates"]["coordinate"]
            folium.PolyLine([(p["latitude"], p["longitude"]) for p in pts], color=COLORS[status],
                            weight=WEIGHT[status], opacity=0.8, tooltip=label).add_to(m)
        folium.CircleMarker((r["lat"], r["lon"]), radius=5, color=COLORS[status], fill=True,
                            fill_opacity=0.9, popup=folium.Popup(info, max_width=320),
                            tooltip=label).add_to(m)

out = C.DOCS / "map_selected.html"
m.save(str(out))
print("Đã tạo", out, "- mở bằng trình duyệt.")
