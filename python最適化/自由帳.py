import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

shp_file_path = "C:\\Users\\hyo15\\remote_nohi_11_16\\市町村界_ポリゴン_JGD2000_11.shp"

# シェープファイルを読み込む
gdf = gpd.read_file(shp_file_path, encoding='shift-jis')

# 最初の数行を表示して、列名を確認
print(gdf.head())

