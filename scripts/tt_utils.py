"""Hàm dùng chung: gọi TomTom Flow Segment Data, tính độ dài/tỷ lệ trong khung,
sinh mã đoạn, và các hàm đọc thuộc tính OSM."""
import hashlib
import math
import re
import time

import requests

FLOW_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{zoom}/json"


# ---------- hình học ----------
def hav(lat1, lon1, lat2, lon2):
    """Khoảng cách (m) giữa hai tọa độ (công thức Haversine)."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def polyline_length(pts):
    """pts: danh sách dict {'latitude','longitude'}. Trả về độ dài (m)."""
    return sum(
        hav(pts[i]["latitude"], pts[i]["longitude"], pts[i + 1]["latitude"], pts[i + 1]["longitude"])
        for i in range(len(pts) - 1)
    )


def inside_ratio(pts, bbox):
    """Tỷ lệ chiều dài (0-1) của đường gấp khúc nằm trong khung bbox (tính theo trung điểm từng đoạn nhỏ)."""
    total = inside = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = hav(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
        mlat = (a["latitude"] + b["latitude"]) / 2
        mlon = (a["longitude"] + b["longitude"]) / 2
        total += d
        if bbox["south"] <= mlat <= bbox["north"] and bbox["west"] <= mlon <= bbox["east"]:
            inside += d
    return inside / total if total > 0 else 0.0


def api_seg_id(pts):
    """Mã nhận diện đoạn TomTom: băm tọa độ điểm đầu và điểm cuối (làm tròn 4 chữ số thập phân).
    Hai lần gọi trả về cùng một đoạn sẽ có cùng mã."""
    a, b = pts[0], pts[-1]
    s = f"{a['latitude']:.4f},{a['longitude']:.4f}|{b['latitude']:.4f},{b['longitude']:.4f}"
    return "T" + hashlib.md5(s.encode()).hexdigest()[:8]


# ---------- gọi API ----------
def fetch_flow(lat, lon, key, zoom=12, retries=3, timeout=15):
    """Trả về (http_status, flowSegmentData hoặc None). Thử lại khi 429/5xx/timeout."""
    wait = 2
    status = None
    for _ in range(retries):
        try:
            r = requests.get(FLOW_URL.format(zoom=zoom), params={"key": key, "point": f"{lat},{lon}"}, timeout=timeout)
            status = r.status_code
            if status == 200:
                return status, r.json()["flowSegmentData"]
            if status not in (429, 500, 502, 503, 504):
                return status, None
        except requests.RequestException:
            status = -1  # lỗi mạng/timeout
        time.sleep(wait)
        wait *= 2
    return status, None


def summarize_flow(d, bbox):
    """Rút gọn một flowSegmentData thành các cột dùng trong CSV."""
    pts = d["coordinates"]["coordinate"]
    return {
        "current_speed": d.get("currentSpeed"),
        "free_flow_speed": d.get("freeFlowSpeed"),
        "current_travel_time": d.get("currentTravelTime"),
        "free_flow_travel_time": d.get("freeFlowTravelTime"),
        "confidence": d.get("confidence"),
        "road_closure": d.get("roadClosure"),
        "api_seg_id": api_seg_id(pts),
        "api_seg_length_m": round(polyline_length(pts)),
        "api_seg_inside_ratio": round(inside_ratio(pts, bbox), 3),
        "api_start_lat": pts[0]["latitude"],
        "api_start_lon": pts[0]["longitude"],
        "api_end_lat": pts[-1]["latitude"],
        "api_end_lon": pts[-1]["longitude"],
        "n_points": len(pts),
    }


# ---------- thuộc tính OSM ----------
def first(v):
    """OSM đôi khi trả về danh sách; lấy phần tử đầu."""
    if isinstance(v, (list, tuple)):
        return v[0] if len(v) else None
    return v


def parse_int(v):
    """'2' -> 2, ['2','3'] -> 2, nan/None -> None."""
    v = first(v)
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    m = re.match(r"\s*(\d+)", str(v))
    return int(m.group(1)) if m else None


def parse_maxspeed(v):
    """'50' -> 50, '30 mph' -> 48, thiếu -> None."""
    v = first(v)
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    s = str(v)
    m = re.match(r"\s*(\d+)", s)
    if not m:
        return None
    n = int(m.group(1))
    return round(n * 1.609) if "mph" in s.lower() else n
