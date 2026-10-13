"""Bước 2c: chọn các đoạn TomTom khác nhau, đạt tiêu chí, từ kết quả probe.
Đầu vào : data/processed/osm_candidates.csv, data/processed/candidates_probed.csv
Đầu ra  : data/processed/osm_segments.csv      (các đoạn được chọn, S001...)
          data/processed/selection_report.csv  (mọi ứng viên + trạng thái + lý do)
          data/processed/segment_owners.csv    (ai kiểm tra đoạn nào)
Chạy:   python scripts/step2c_select.py
Loại một số đoạn sau khi họp (đoạn sai) rồi chọn lại:
        python scripts/step2c_select.py --exclude C012,C033
KHÔNG tốn request TomTom.
"""
import argparse
import sys

import pandas as pd

import config as C

ap = argparse.ArgumentParser()
ap.add_argument("--exclude", default="", help="Danh sách candidate_id loại bỏ, cách nhau dấu phẩy")
args = ap.parse_args()
excluded = {x.strip() for x in args.exclude.split(",") if x.strip()}

cands = pd.read_csv(C.DATA_PROC / "osm_candidates.csv")
probed = pd.read_csv(C.DATA_PROC / "candidates_probed.csv")
df = cands.merge(probed, on="candidate_id", how="left")


def reason(r):
    """Trả về lý do loại, hoặc '' nếu đạt tiêu chí."""
    if r["candidate_id"] in excluded:
        return "loại thủ công sau kiểm tra"
    if r["http_status"] != 200:
        return f"API lỗi ({r['http_status']})"
    if r["confidence"] < C.MIN_CONFIDENCE:
        return f"confidence thấp ({r['confidence']:.2f})"
    if r["api_seg_inside_ratio"] < C.MIN_INSIDE_RATIO:
        return f"đoạn nằm ngoài Bình Thạnh nhiều (trong {r['api_seg_inside_ratio']:.2f})"
    if r["api_seg_length_m"] > C.MAX_API_SEG_LENGTH_M:
        return f"đoạn quá dài ({int(r['api_seg_length_m'])} m)"
    return ""


df["reject_reason"] = df.apply(reason, axis=1)
ok = df[df["reject_reason"] == ""].copy()

# Xếp hạng: nằm trong khung nhiều hơn -> đoạn ngắn hơn -> confidence cao hơn
ok["inside_bucket"] = (ok["api_seg_inside_ratio"] * 10).round() / 10
ok = ok.sort_values(["inside_bucket", "api_seg_length_m", "confidence"], ascending=[False, True, False])

# Loại trùng: nhiều ứng viên cùng ra một đoạn TomTom -> giữ cái xếp hạng cao nhất
dup_mask = ok.duplicated("api_seg_id", keep="first")
dups = ok[dup_mask]
ok = ok[~dup_mask]

selected = ok.head(C.N_SEGMENTS)
backup = ok.iloc[C.N_SEGMENTS:C.N_SEGMENTS + C.N_BACKUP]

df["status"] = "rejected"
df.loc[df["candidate_id"].isin(dups["candidate_id"]), "status"] = "duplicate"
df.loc[df["candidate_id"].isin(backup["candidate_id"]), "status"] = "backup"
df.loc[df["candidate_id"].isin(selected["candidate_id"]), "status"] = "selected"
df.loc[df["status"] == "duplicate", "reject_reason"] = "trùng đoạn TomTom với ứng viên xếp hạng cao hơn"
df.loc[(df["status"] == "rejected") & (df["reject_reason"] == ""), "reject_reason"] = "dư so với số đoạn tối đa"

# Đặt mã S001... cho đoạn được chọn (sắp theo tên đường cho dễ tra)
selected = selected.sort_values(["street_name", "lat"]).reset_index(drop=True)
selected.insert(0, "segment_id", [f"S{i + 1:03d}" for i in range(len(selected))])

seg_cols = ["segment_id", "candidate_id", "osm_way_id", "street_name", "highway_type", "lanes",
            "maxspeed_kmh", "oneway", "length_m", "lat", "lon",
            "api_seg_id", "api_seg_length_m", "api_seg_inside_ratio"]
C.DATA_PROC.mkdir(parents=True, exist_ok=True)
for col in ("lanes", "maxspeed_kmh", "length_m", "api_seg_length_m"):   # tránh ghi 3.0 thay vì 3
    selected[col] = selected[col].round().astype("Int64")
selected[seg_cols].to_csv(C.DATA_PROC / "osm_segments.csv", index=False, encoding="utf-8")

rep_cols = ["candidate_id", "status", "reject_reason", "street_name", "highway_type", "lat", "lon",
            "http_status", "confidence", "current_speed", "free_flow_speed",
            "api_seg_id", "api_seg_length_m", "api_seg_inside_ratio"]
order = {"selected": 0, "backup": 1, "duplicate": 2, "rejected": 3}
df["api_seg_length_m"] = df["api_seg_length_m"].round().astype("Int64")
df.assign(_o=df["status"].map(order)).sort_values(["_o", "candidate_id"])[rep_cols] \
    .to_csv(C.DATA_PROC / "selection_report.csv", index=False, encoding="utf-8")

# Chia người kiểm tra: liên tiếp, người cuối nhận phần dư (25 đoạn -> 3,3,3,3,3,3,3,4)
n = len(selected)
base, rem = divmod(n, C.N_OWNERS)
sizes = [base + (1 if i >= C.N_OWNERS - rem else 0) for i in range(C.N_OWNERS)]
owners = []
for person, size in enumerate(sizes, start=1):
    owners += [person] * size
pd.DataFrame({"segment_id": selected["segment_id"], "street_name": selected["street_name"],
              "owner": owners}).to_csv(C.DATA_PROC / "segment_owners.csv", index=False, encoding="utf-8")

# Tóm tắt
print(f"Ứng viên: {len(df)} | probe thành công: {int((df['http_status'] == 200).sum())}")
print("Lý do loại (đếm):")
print(df.loc[df["status"].isin(["rejected", "duplicate"]), "reject_reason"].str.replace(r"\(.*\)", "", regex=True).value_counts().to_string())
print(f"\nĐã chọn {len(selected)} đoạn, dự phòng {len(backup)}.")
print(f"Số mẫu dự kiến: {len(selected)} x {C.RUNS_PER_DAY} x {C.DAYS} = {len(selected) * C.RUNS_PER_DAY * C.DAYS}")
print("Chia người kiểm tra:", sizes)
if len(selected) < C.N_SEGMENTS_MIN:
    print(f"\nCẢNH BÁO: chỉ có {len(selected)} đoạn (< {C.N_SEGMENTS_MIN}). Báo leader: cần nới MIN_INSIDE_RATIO / "
          "MAX_API_SEG_LENGTH_M / MIN_CONFIDENCE trong scripts/config.py rồi chạy lại.")
    sys.exit(1)
