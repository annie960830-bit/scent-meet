import pandas as pd
import sqlite3

df = pd.read_csv("perfumes.csv", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

conn = sqlite3.connect("perfumes.db")

df.to_sql("perfumes", conn, if_exists="replace", index=False)

conn.close()

print("CSV 已成功匯入 perfumes.db")