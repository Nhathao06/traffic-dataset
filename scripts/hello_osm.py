"""Kiểm tra OSMnx: tải mạng đường quanh Bình Thạnh và đếm theo loại đường.
Chạy:  python scripts/hello_osm.py
(Dùng tâm + bán kính thay vì tên quận, vì ranh giới hành chính ở TP.HCM đã
thay đổi và OSM có thể không còn đối tượng 'Quận Bình Thạnh'.)
"""
import osmnx as ox
from config import AREA_BBOX as B, AREA_CENTER, AREA_RADIUS_M, HIGHWAY_TYPES

G = ox.graph_from_point(AREA_CENTER, dist=AREA_RADIUS_M, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False).reset_index()
print("Tổng số cạnh tải về:", len(edges))

edges["hw"] = edges["highway"].apply(lambda x: x[0] if isinstance(x, list) else x)
main = edges[edges["hw"].isin(HIGHWAY_TYPES)]
c = main.geometry.centroid
inside = main[(c.y >= B["south"]) & (c.y <= B["north"]) & (c.x >= B["west"]) & (c.x <= B["east"])]
print(f"Cạnh {HIGHWAY_TYPES} trong khung bao Bình Thạnh:", len(inside))
print(inside["hw"].value_counts())
print("Một số tên đường:", sorted({str(n) for n in inside.get("name", []) if n == n})[:10])
print("\nOK: OSMnx hoạt động.")
