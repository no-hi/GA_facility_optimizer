import os
import pandas as pd
import xlsxwriter
import numpy as np

# ディレクトリパスの取得
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "data.py")

# data.py のデータを読み込む
with open(data_dir, "r", encoding="utf-8") as f:
    exec(f.read())

# 市町村名のリストを一つ右にずらす
name_shifted = [''] + name[:-1]

# 距離リストを179x179の行列に変換
distance_matrix = np.zeros((179, 179))

for i in range(179):
    for j in range(179):
        distance_matrix[i][j] = float(distance[i * 179 + j])

# データフレームの作成
df = pd.DataFrame(distance_matrix, columns=name_shifted, index=name)

# エクセルファイルの作成
filename = "distance.xlsx"  # ファイル名を指定
workbook = xlsxwriter.Workbook(filename)
worksheet = workbook.add_worksheet()

# データフレームをエクセルファイルに書き込む
row = 0
col = 1

# 列名を書き込む
for i, col_name in enumerate(df.columns):
    worksheet.write(row, col + i, col_name)

# 行名とデータを書き込む
for i, row_name in enumerate(df.index):
    worksheet.write(row + i + 1, col - 1, row_name)
    worksheet.write_row(row + i + 1, col, df.iloc[i])

workbook.close()

print("エクセルファイルが作成されました。")
