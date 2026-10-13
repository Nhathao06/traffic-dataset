"""Quét lưới 3x4 điểm trong khung bao Bình Thạnh (tốn 12 request).
Mục đích: xem đoạn TomTom trả về dài bao nhiêu, nằm trong/ngoài Bình Thạnh,
và các điểm khác nhau có trả về CÙNG một đoạn không.
Chạy:  python scripts/probe_grid.py
"""
import math
import os
import time

import requests
from dotenv import load_dotenv
from config import AREA_BBOX as B

load_dotenv()
KEY = os.getenv("TOMTOM_API_KEY")
URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/12/json"


def hav(a, b):
    r = 6371000
    p1, p2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dp = p2 - p1
    dl = math.radians(b["longitude"] - a["longitude"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def inside(p):
    return B["south"] <= p["latitude"] <= B["north"] and B["west"] <= p["longitude"] <= B["east"]


lats = [B["south"] + (B["north"] - B["south"]) * f for f in (0.2, 0.5, 0.8)]
lons = [B["west"] + (B["east"] - B["west"]) * f for f in (0.2, 0.4, 0.6, 0.8)]

seen = {}
for la in lats:
    for lo in lons:
        r = requests.get(URL, params={"key": KEY, "point": f"{la:.5f},{lo:.5f}"}, timeout=15)
        if r.status_code != 200:
            print(f"({la:.4f},{lo:.4f}) lỗi {r.status_code}")
            time.sleep(0.3)
            continue
        d = r.json()["flowSegmentData"]
        pts = d["coordinates"]["coordinate"]
        length = sum(hav(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        key = (round(pts[0]["latitude"], 4), round(pts[0]["longitude"], 4))
        seen[key] = seen.get(key, 0) + 1
        where = "trong" if inside(pts[0]) and inside(pts[-1]) else "RA NGOÀI/một phần"
        print(f"hỏi ({la:.4f},{lo:.4f}) -> dài {length:6.0f} m | {where:18} | "
              f"{d['currentSpeed']}/{d['freeFlowSpeed']} km/h | "
              f"đầu {key} cuối ({pts[-1]['latitude']:.4f},{pts[-1]['longitude']:.4f})")
        time.sleep(0.3)

print(f"\n12 điểm hỏi -> {len(seen)} đoạn TomTom khác nhau")
