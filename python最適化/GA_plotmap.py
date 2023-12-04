import data
import matplotlib.pyplot as plt
import geopandas as gpd

hokkaido = data.name

# 北海道の地図データを取得（例）
hokkaido_map = gpd.read_file("hokkaido_map_data.shp")

# 市町村名のリスト（例）
hokkaido = ["札幌市", "函館市", "旭川市", "...", "その他の市町村..."]

# best_individual.inc_facilityに含まれる番号（例）
best_individual = {
    "inc_facility": [0, 3, 7, 10]  # これは例です
}

# 施設の位置を特定
facility_locations = [hokkaido[i] for i in best_individual["inc_facility"]]

# 北海道の地図をプロット
hokkaido_map.plot()

# 各施設の位置をプロット
for location in facility_locations:
    # 市町村の位置情報を取得（緯度、経度）
    lat, lon = get_location_coordinates(location)  # この関数は実装する必要があります
    plt.plot(lon, lat, 'ro')  # 赤い点で位置を表示

plt.show()
