"""Kiểm tra môi trường: gọi 1 request TomTom Flow Segment Data tại Bình Thạnh.
Chạy:  python scripts/hello_tomtom.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("TOMTOM_API_KEY")
if not KEY or KEY == "your_key_here":
    sys.exit("Chưa có TOMTOM_API_KEY trong file .env")

# Điểm thử: khu vực ngã tư Hàng Xanh, Bình Thạnh (xấp xỉ)
LAT, LON = 10.8018, 106.7112
URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

resp = requests.get(URL, params={"key": KEY, "point": f"{LAT},{LON}"}, timeout=15)
print("HTTP status:", resp.status_code)
if resp.status_code != 200:
    sys.exit(f"Lỗi: {resp.text[:300]}")

d = resp.json()["flowSegmentData"]
print("currentSpeed (km/h)      :", d.get("currentSpeed"))
print("freeFlowSpeed (km/h)     :", d.get("freeFlowSpeed"))
print("currentTravelTime (s)    :", d.get("currentTravelTime"))
print("freeFlowTravelTime (s)   :", d.get("freeFlowTravelTime"))
print("confidence               :", d.get("confidence"))
print("roadClosure              :", d.get("roadClosure"))
pts = d.get("coordinates", {}).get("coordinate", [])
print("Số điểm hình học đoạn    :", len(pts))
if pts:
    print("Điểm đầu đoạn API trả về :", pts[0])
print("\nOK. Sau vài phút, dòng 'Traffic Flow Segment Data API' trên dashboard phải tăng lên.")
print("Mỗi lần chạy script này tốn 1 request trong hạn mức 20.000/tháng của key bạn.")
