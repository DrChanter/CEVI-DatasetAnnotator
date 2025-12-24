"""
gui.py
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Literal, Tuple, cast

import gradio as gr

from get_file import Pair, PicData

DATA_FILE = Path("./database.db")


def load_data() -> List[Tuple]:
    """
    加载数据库中的记录
    """
    try:
        conn = sqlite3.connect(DATA_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        _records = cursor.fetchall()
        conn.close()
    except Exception as e:
        raise LookupError("未能接入到 SQL") from e
    return _records


def to_pair(_records) -> List[Pair]:
    """
    将数据库中的记录转换为 Pair 类型
    """
    _pairs = []
    for record in _records:
        pair = Pair()
        pair.load_from_tuple(record)
        _pairs.append(pair)
    return _pairs


def submit(
    pair_idx: int,
    weather: str,
    feature: List[str],
    shooting_position_x: float,
    shooting_position_y: float,
    temperature: int,
    humidity: int,
    precip: float,
    pressure: int,
    visibility: int,
    cloud_cover: int,
    wind_dir: str,
    wind_scale: int,
    wind_speed: int,
) -> str:
    """
    处理提交按钮的事件
    """
    pair: Pair = pairs[pair_idx]
    pair.data.weather = weather
    pair.data.feature = cast(
        List[
            Literal[
                "forest",
                "water",
                "grass",
                "bare",
                "farmland",
                "road",
                "building",
                "beach",
            ]
        ],
        feature,
    )
    pair.data.shooting_position = (shooting_position_x, shooting_position_y)
    pair.data.temperature = temperature
    pair.data.humidity = humidity
    pair.data.precip = precip
    pair.data.pressure = pressure
    pair.data.vis = visibility
    pair.data.cloud = cloud_cover
    pair.data.wind_dir = wind_dir
    pair.data.wind_scale = wind_scale
    pair.data.wind_speed = wind_speed

    pair.data.dump()

    conn: sqlite3.Connection = sqlite3.connect(database=DATA_FILE)
    cursor: sqlite3.Cursor = conn.cursor()

    cursor.execute(
        """
    UPDATE records SET
        original=?,
        processed=?,
        time_stamp=?,
        feature=?,
        shooting_position=?,
        wind_dir=?,
        wind_scale=?,
        wind_speed=?,
        humidity=?,
        precip=?,
        pressure=?,
        vis=?,
        cloud=?,
        `AS`=?,
        `HS`=?,
        weather=?,
        temperature=?
    WHERE original=?
    """,
        (
            str(pair.original),
            str(pair.processed),
            pair.data.time_stamp,
            json.dumps(pair.data.feature, ensure_ascii=False),
            json.dumps(pair.data.shooting_position, ensure_ascii=False),
            pair.data.wind_dir,
            pair.data.wind_scale,
            pair.data.wind_speed,
            pair.data.humidity,
            pair.data.precip,
            pair.data.pressure,
            pair.data.vis,
            pair.data.cloud,
            pair.data.AS,
            pair.data.HS,
            pair.data.weather,
            pair.data.temperature,
            str(pair.original),
        ),
    )
    conn.commit()
    conn.close()
    return json.dumps(pairs[pair_idx].data.dump(), indent=4, ensure_ascii=False)


def submit_and_next(
    pair_idx: int,
    weather: str,
    feature: List[str],
    shooting_position_x: float,
    shooting_position_y: float,
    temperature: int,
    humidity: int,
    precip: float,
    pressure: int,
    visibility: int,
    cloud_cover: int,
    wind_dir: str,
    wind_scale: int,
    wind_speed: int,
) -> tuple[int, str]:
    """
    处理提交并加载下一张按钮的事件
    """
    result = submit(
        pair_idx=pair_idx,
        weather=weather,
        feature=feature,
        shooting_position_x=shooting_position_x,
        shooting_position_y=shooting_position_y,
        temperature=temperature,
        humidity=humidity,
        precip=precip,
        pressure=pressure,
        visibility=visibility,
        cloud_cover=cloud_cover,
        wind_dir=wind_dir,
        wind_scale=wind_scale,
        wind_speed=wind_speed,
    )
    pair_idx = (pair_idx + 1) % len(pairs)
    return (pair_idx, result)


def main() -> None:
    """
    主函数
    """

    with gr.Blocks() as app:
        gr.Markdown("## 工具")

        # GUI 设计
        with gr.Tab(label="单张"):
            # 图像和数据展示
            with gr.Row():
                image_original = gr.Image(type="filepath", label="原始图像")
                image_processed = gr.Image(type="filepath", label="红外图像")
                label_data = gr.Textbox(value="", label="图像数据")

            # 打标部分
            with gr.Row():
                with gr.Column():
                    weather = gr.Dropdown(
                        value="sunny",
                        choices=[
                            ("晴", "sunny"),
                            ("阴", "overcast"),
                            ("多云", "cloudy"),
                            ("雨", "rainy"),
                            ("雪", "snowy"),
                            ("雾", "foggy"),
                        ],
                        label="天气",
                    )

                    feature = gr.CheckboxGroup(
                        choices=PicData.FEATURE_TYPE, label="地物类型"
                    )
                    with gr.Column():
                        shooting_position_x = gr.Number(label="拍摄位置 (经度)")
                        shooting_position_y = gr.Number(label="拍摄位置 (纬度)")

                with gr.Column():
                    with gr.Column():
                        temperature = gr.Slider(
                            value=-50,
                            minimum=-50,
                            maximum=50,
                            step=1,
                            label="温度 (°C)",
                        )
                        humidity = gr.Slider(
                            value=0, minimum=0, maximum=100, step=1, label="湿度 (%)"
                        )
                        precip = gr.Number(value=0.0, label="降水量 (mm)")
                        pressure = gr.Number(value=0, label="气压 (hPa)")
                        visibility = gr.Number(value=0, label="能见度 (m)")
                        cloud_cover = gr.Slider(
                            value=0, minimum=0, maximum=100, step=1, label="云量 (%)"
                        )

                with gr.Column():
                    wind_dir = gr.Dropdown(
                        value="北风",
                        choices=[
                            "北风",
                            "东风",
                            "南风",
                            "西风",
                            "东北风",
                            "东南风",
                            "西北风",
                            "西南风",
                        ],
                        label="风向",
                    )
                    wind_scale = gr.Slider(
                        minimum=0, maximum=12, step=1, label="风力等级"
                    )
                    wind_speed = gr.Slider(
                        minimum=0, maximum=100, step=1, label="风速 (km/h)"
                    )

            # 图像选择
            with gr.Row():
                pair_idx = gr.Slider(
                    minimum=0,
                    maximum=len(pairs) - 1,
                    label="图像编号",
                    key="image_index",
                    step=1,
                )

                def update_images(index):
                    print(pairs[index].original, pairs[index].processed)
                    image_original.value = str(pairs[index].original)
                    image_processed.value = str(pairs[index].processed)
                    label_data.value = json.dumps(
                        pairs[index].data.dump(), indent=4, ensure_ascii=False
                    )
                    if pairs[index].data.weather:
                        weather.value = pairs[index].data.weather
                    if pairs[index].data.feature:
                        feature.value = pairs[index].data.feature
                    if pairs[index].data.shooting_position[0] != 0.0:
                        shooting_position_x.value = pairs[index].data.shooting_position[
                            0
                        ]
                    if pairs[index].data.shooting_position[1] != 0.0:
                        shooting_position_y.value = pairs[index].data.shooting_position[
                            1
                        ]
                    if pairs[index].data.temperature:
                        temperature.value = pairs[index].data.temperature
                    if pairs[index].data.humidity != 0:
                        humidity.value = pairs[index].data.humidity
                    if pairs[index].data.precip != 0.0:
                        precip.value = pairs[index].data.precip
                    if pairs[index].data.pressure != 0:
                        pressure.value = pairs[index].data.pressure
                    if pairs[index].data.vis != 0:
                        visibility.value = pairs[index].data.vis
                    if pairs[index].data.cloud != 0:
                        cloud_cover.value = pairs[index].data.cloud
                    if pairs[index].data.wind_dir:
                        wind_dir.value = pairs[index].data.wind_dir
                    if pairs[index].data.wind_scale != 0:
                        wind_scale.value = pairs[index].data.wind_scale
                    if pairs[index].data.wind_speed != 0:
                        wind_speed.value = pairs[index].data.wind_speed
                    return (
                        image_original.value,
                        image_processed.value,
                        label_data.value,
                    )

                pair_idx.change(  # pylint: disable=no-member
                    fn=update_images,
                    inputs=pair_idx,
                    outputs=[
                        image_original,
                        image_processed,
                        label_data,
                    ],
                )

                submit_btn = gr.Button("提交", variant="primary")

                submit_and_next_btn = gr.Button("提交并加载下一张", variant="primary")

            submit_btn.click(  # pylint: disable=no-member
                fn=submit,
                inputs=[
                    pair_idx,
                    weather,
                    feature,
                    shooting_position_x,
                    shooting_position_y,
                    temperature,
                    humidity,
                    precip,
                    pressure,
                    visibility,
                    cloud_cover,
                    wind_dir,
                    wind_scale,
                    wind_speed,
                ],
                outputs=label_data,
            )

            submit_and_next_btn.click(  # pylint: disable=no-member
                fn=submit_and_next,
                inputs=[
                    pair_idx,
                    weather,
                    feature,
                    shooting_position_x,
                    shooting_position_y,
                    temperature,
                    humidity,
                    precip,
                    pressure,
                    visibility,
                    cloud_cover,
                    wind_dir,
                    wind_scale,
                    wind_speed,
                ],
                outputs=[pair_idx, label_data],
            )

    app.launch()


if __name__ == "__main__":
    records = load_data()
    pairs: List[Pair] = to_pair(records)
    main()
