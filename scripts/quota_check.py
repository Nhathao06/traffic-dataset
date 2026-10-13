"""Đếm số request đã gọi theo ngày từ traffic_raw.csv và so với hạn mức.
Chạy:  python scripts/quota_check.py [đường_dẫn_csv]
"""
import sys

import pandas as pd
from config import EXPECTED_SAMPLES, HARD_CAP_ROWS, MAX_SAMPLES, MONTHLY_QUOTA, RUNS_PER_DAY, N_SEGMENTS

path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/traffic_raw.csv"
df = pd.read_csv(path, parse_dates=["collected_at"])
per_day = df.groupby(df["collected_at"].dt.date).size()
exp_day = N_SEGMENTS * RUNS_PER_DAY

print("Số dòng theo ngày (kỳ vọng %d/ngày):" % exp_day)
print(per_day.to_string())
print("\nMã HTTP:\n", df["http_status"].value_counts().to_string())
n = len(df)
print(f"\nTổng dòng: {n} | kỳ vọng cả đợt: {EXPECTED_SAMPLES} | trần đề bài: {MAX_SAMPLES} | collector dừng ở: {HARD_CAP_ROWS}")
print(f"Đã dùng ~{n} request = {n / MONTHLY_QUOTA:.1%} hạn mức tháng ({MONTHLY_QUOTA}) (chưa tính request test)")
if n > HARD_CAP_ROWS:
    print("CẢNH BÁO: vượt ngưỡng dừng của collector!")
if (df["http_status"] == 429).any():
    print("CẢNH BÁO: có mã 429 (quá hạn mức hoặc quá QPS) -> tăng REQUEST_DELAY_S.")
