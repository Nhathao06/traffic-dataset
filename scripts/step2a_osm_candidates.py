"""Bước 2a: tạo ~60 điểm ứng viên từ OpenStreetMap quanh Bình Thạnh.
Kết quả: data/processed/osm_candidates.csv   (KHÔNG tốn request TomTom)
Chạy:  python scripts/step2a_osm_candidates.py
"""
import geopandas as gpd
import osmnx as ox
import pandas as pd

import config as C
from tt_utils import first, parse_int, parse_maxspeed

TYPE_PRIORITY = {"trunk": 0, "primary": 1, "secondary": 2}

print("Đang tải mạng đường từ OSM (có thể mất vài phút)...")
G = ox.graph_from_point(C.AREA_CENTER, dist=C.AREA_RADIUS_M, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False).reset_index(drop=True)
print("Tổng số cạnh:", len(edges))

edges["highway_type"] = edges["highway"].apply(first)
edges = edges[edges["highway_type"].isin(C.HIGHWAY_TYPES)].copy()
edges["street_name"] = edges["name"].apply(first) if "name" in edges.columns else None
edges = edges[edges["street_name"].notna()].copy()

# Tính độ dài và trung điểm trong hệ tọa độ mét (UTM 48N)
proj = edges.to_crs(32648)
edges["length_m"] = proj.geometry.length.round(0)
mid = proj.geometry.interpolate(0.5, normalized=True)
edges["x"], edges["y"] = mid.x, mid.y
mid_ll = gpd.GeoSeries(mid, crs=32648).to_crs(4326)
edges["lat"], edges["lon"] = mid_ll.y.round(6), mid_ll.x.round(6)

B = C.AREA_BBOX
edges = edges[(edges["lat"].between(B["south"], B["north"])) & (edges["lon"].between(B["west"], B["east"]))]
edges = edges[edges["length_m"] >= C.OSM_MIN_EDGE_M].copy()
print("Cạnh phù hợp (đúng loại, có tên, trong khung, đủ dài):", len(edges))

edges["osm_way_id"] = edges["osmid"].apply(lambda v: str(first(v)))
edges["lanes"] = edges["lanes"].apply(parse_int) if "lanes" in edges.columns else None
edges["maxspeed_kmh"] = edges["maxspeed"].apply(parse_maxspeed) if "maxspeed" in edges.columns else None
edges["oneway"] = edges["oneway"].apply(lambda v: bool(first(v)))
# một đường (osm_way_id) có thể gồm nhiều cạnh: giữ cạnh dài nhất mỗi way
edges = edges.sort_values("length_m", ascending=False).drop_duplicates("osm_way_id")

# Với mỗi tên đường, chọn tối đa MAX_PER_STREET điểm cách nhau >= MIN_SPACING_M
picked = []
for name, grp in edges.groupby("street_name"):
    taken = []
    for row in grp.sort_values("length_m", ascending=False).itertuples():
        if all(((row.x - t.x) ** 2 + (row.y - t.y) ** 2) ** 0.5 >= C.MIN_SPACING_M for t in taken):
            taken.append(row)
        if len(taken) >= C.MAX_PER_STREET:
            break
    for rank, row in enumerate(taken):
        picked.append({**row._asdict(), "rank_in_street": rank})
pool = pd.DataFrame(picked)
pool["type_priority"] = pool["highway_type"].map(TYPE_PRIORITY)
pool = pool.sort_values(["rank_in_street", "type_priority", "length_m"], ascending=[True, True, False])
pool = pool.head(C.N_CANDIDATES).sort_values(["street_name", "lat"]).reset_index(drop=True)
pool["candidate_id"] = [f"C{i + 1:03d}" for i in range(len(pool))]

cols = ["candidate_id", "osm_way_id", "street_name", "highway_type", "lanes",
        "maxspeed_kmh", "oneway", "length_m", "lat", "lon"]
for col in ("lanes", "maxspeed_kmh", "length_m"):   # số nguyên, cho phép thiếu
    pool[col] = pd.to_numeric(pool[col], errors="coerce").round().astype("Int64")
C.DATA_PROC.mkdir(parents=True, exist_ok=True)
out = C.DATA_PROC / "osm_candidates.csv"
pool[cols].to_csv(out, index=False, encoding="utf-8")
print(f"\nĐã ghi {len(pool)} ứng viên -> {out}")
print("Số tên đường khác nhau:", pool["street_name"].nunique())
print(pool["highway_type"].value_counts().to_string())
print("Thiếu lanes:", int(pool["lanes"].isna().sum()), "| thiếu maxspeed:", int(pool["maxspeed_kmh"].isna().sum()))
if len(pool) < C.N_CANDIDATES:
    print("LƯU Ý: ít hơn", C.N_CANDIDATES, "ứng viên. Báo leader để nới MAX_PER_STREET hoặc khung bao.")
