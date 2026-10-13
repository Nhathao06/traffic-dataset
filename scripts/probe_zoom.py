"""Thử các mức zoom để xem độ dài đoạn TomTom trả về (tốn 5 request)."""
import math
import os

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("TOMTOM_API_KEY")
LAT, LON = 10.8018, 106.7112


def hav(a, b):
    r = 6371000
    p1, p2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dp = p2 - p1
    dl = math.radians(b["longitude"] - a["longitude"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


for z in (10, 12, 14, 16, 18):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{z}/json"
    resp = requests.get(url, params={"key": KEY, "point": f"{LAT},{LON}"}, timeout=15)
    if resp.status_code != 200:
        print(f"zoom {z}: lỗi {resp.status_code}")
        continue
    d = resp.json()["flowSegmentData"]
    pts = d["coordinates"]["coordinate"]
    length = sum(hav(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    print(f"zoom {z}: dài ~{length:.0f} m | {len(pts)} điểm | "
          f"tốc độ {d['currentSpeed']}/{d['freeFlowSpeed']} km/h | "
          f"điểm đầu {pts[0]['latitude']:.4f},{pts[0]['longitude']:.4f}")
