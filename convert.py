"""
convert.py
"""

import json
import sqlite3
from pathlib import Path
from typing import Any


def convert_to_sqlite(data_file: Path, database_file: Path) -> None:
    """
    将JSON数据转换为SQLite数据库
    """
    # 读取JSON数据
    with open(file=data_file, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    # 删除旧的数据库文件
    database_file.unlink(missing_ok=True)

    # 创建SQLite数据库和表
    conn: sqlite3.Connection = sqlite3.connect(database=database_file)
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY,
        original TEXT,
        processed TEXT,
        time_stamp TEXT,
        feature TEXT,
        shooting_position TEXT,
        wind_dir TEXT,
        wind_scale INTEGER,
        wind_speed INTEGER,
        humidity INTEGER,
        precip REAL,
        pressure INTEGER,
        vis INTEGER,
        cloud INTEGER,
        `AS` REAL,
        `HS` REAL,
        weather TEXT,
        temperature REAL
    )
    """)

    # 插入数据
    for record in data["RECORDS"]:
        cursor.execute(
            """
        INSERT INTO records (
            original, processed, time_stamp, feature, shooting_position, 
            wind_dir, wind_scale, wind_speed, humidity, precip, pressure, 
            vis, cloud, `AS`, `HS`, weather, temperature
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record["original"],
                record["processed"],
                record["time_stamp"],
                json.dumps(record["feature"], ensure_ascii=False),
                json.dumps(record["shooting_position"], ensure_ascii=False),
                record["wind_dir"],
                record["wind_scale"],
                record["wind_speed"],
                record["humidity"],
                record["precip"],
                record["pressure"],
                record["vis"],
                record["cloud"],
                record["AS"],
                record["HS"],
                record["weather"],
                record["temperature"],
            ),
        )

    # 提交并关闭
    conn.commit()
    conn.close()


def convert_to_json(database_file: Path, output_file: Path) -> None:
    """
    将SQLite数据库转换为JSON数据
    """
    conn: sqlite3.Connection = sqlite3.connect(database_file)
    cursor: sqlite3.Cursor = conn.cursor()

    cursor.execute("SELECT * FROM records")
    records: list[Any] = cursor.fetchall()

    columns: list[str | Any] = [column[0] for column in cursor.description]

    data: dict[str, Any] = {"RECORDS": []}
    for record in records:
        record_dict = dict(zip(columns, record))

        record_dict["feature"] = json.loads(record_dict["feature"])
        record_dict["shooting_position"] = json.loads(record_dict["shooting_position"])

        data["RECORDS"].append(record_dict)

    with open(file=output_file, mode="w", encoding="utf-8") as f:
        json.dump(obj=data, fp=f, ensure_ascii=False, indent=4)

    conn.close()


if __name__ == "__main__":
    _data_file: Path = Path("./database.json")
    _database_file: Path = Path("./database.db")
    convert_to_sqlite(data_file=_data_file, database_file=_database_file)
    print("Done!")
