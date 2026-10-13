"""Bước 2b: gọi TomTom 1 lần cho mỗi điểm ứng viên (~60 request) để biết đoạn TomTom trả về.
Kết quả: data/processed/candidates_probed.csv  +  data/raw/probe/<candidate_id>.json
Chạy:  python scripts/step2b_probe_candidates.py
Chạy lại an toàn: ứng viên đã có kết quả 200 sẽ được bỏ qua (không tốn request).
"""
import json
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv

import config as C
from tt_utils import fetch_flow, summarize_flow

load_dotenv()
KEY = os.getenv("TOMTOM_API_KEY")
if not KEY or KEY == "your_key_here":
    sys.exit("Chưa có TOMTOM_API_KEY trong file .env")

cand_path = C.DATA_PROC / "osm_candidates.csv"
if not cand_path.exists():
    sys.exit(f"Không thấy {cand_path}. Cần chạy step2a (hoặc kéo file từ nhánh của người 1) trước.")
cands = pd.read_csv(cand_path)

out_path = C.DATA_PROC / "candidates_probed.csv"
done = {}
if out_path.exists():
    old = pd.read_csv(out_path)
    done = {r["candidate_id"]: r for r in old.to_dict("records") if r["http_status"] == 200}

probe_dir = C.DATA_RAW / "probe"
probe_dir.mkdir(parents=True, exist_ok=True)
tz = ZoneInfo(C.TIMEZONE)

rows, n_calls = [], 0
for c in cands.to_dict("records"):
    cid = c["candidate_id"]
    if cid in done:
        rows.append(done[cid])
        continue
    status, d = fetch_flow(c["lat"], c["lon"], KEY, zoom=C.ZOOM)
    n_calls += 1
    row = {"candidate_id": cid, "probed_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), "http_status": status}
    if d is not None:
        (probe_dir / f"{cid}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        row.update(summarize_flow(d, C.AREA_BBOX))
        print(f"{cid} {c['street_name'][:22]:22} -> dài {row['api_seg_length_m']:6} m | trong {row['api_seg_inside_ratio']:.2f} | conf {row['confidence']}")
    else:
        print(f"{cid} {c['street_name'][:22]:22} -> LỖI {status}")
    rows.append(row)
    time.sleep(C.REQUEST_DELAY_S)

pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8")
ok = sum(1 for r in rows if r["http_status"] == 200)
print(f"\nĐã gọi {n_calls} request mới. Thành công {ok}/{len(rows)}. -> {out_path}")
if ok < len(rows):
    print("Có ứng viên lỗi: chạy lại script (chỉ gọi lại những cái lỗi).")
