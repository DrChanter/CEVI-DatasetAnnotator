"""
get info
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, List, Literal, Optional

from convert import convert_to_sqlite


class PicData:
    """
    图像数据类。
    """

    WEATHER_REDIRECT: dict[str, str] = {
        "晴": "sunny",
        "阴": "overcast",
        "多云": "cloudy",
        "雨": "rainy",
        "雪": "snowy",
        "雾": "foggy",
    }

    FEATURE_TYPE: list[str] = [
        "forest",
        "water",
        "grass",
        "bare",
        "farmland",
        "road",
        "building",
        "beach",
    ]

    def __init__(self) -> None:
        self.time_stamp: str = ""
        "时间戳"

        self._weather: Optional[
            Literal["sunny", "overcast", "cloudy", "rainy", "snowy", "foggy"]
        ] = None
        "天气"

        self._temperature: Optional[int] = None
        "温度"

        self.feature: Optional[
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
            ]
        ] = None
        "地物类型"

        self.shooting_position: tuple[float, float] = (0.0, 0.0)
        "拍摄位置"

        self.wind_dir: str = ""
        "风向"

        self.wind_scale: int = 0
        "风力"

        self.wind_speed: int = 0
        "风速"

        self.humidity: int = 0
        "湿度"

        self.precip: float = 0.0
        "降水量"

        self.pressure: int = 0
        "气压"

        self.vis: int = 0
        "能见度"

        self.cloud: int = 0
        "云量"

        self.AS: float = 0.0  # pylint: disable=invalid-name

        self.HS: float = 0.0  # pylint: disable=invalid-name

    def __repr__(self) -> str:
        name: str = self.__class__.__name__
        dict_str: str = ", ".join(
            f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        dict_str += f", weather={self._weather}, temperature={self._temperature}"
        return f"{name}({dict_str})"

    @property
    def weather(self) -> str:
        """
        天气
        """
        if self._weather is None:
            return ""
        result: str = self.WEATHER_REDIRECT.get(self._weather, "")
        if not result:
            return self._weather
        return result

    @weather.setter
    def weather(self, value: str) -> None:
        self._weather = value  # pylint: disable=attribute-defined-outside-init   #type: ignore

    @property
    def temperature(self) -> Optional[int]:
        """
        温度
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value: int | str | None) -> None:
        if isinstance(value, str):
            value = int(value)
        self._temperature = value

    def dump(self) -> dict[str, Any]:
        """
        将数据转换为字典。
        """
        data: dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                data[k] = v
        data["weather"] = self.weather
        data["temperature"] = self.temperature
        return data


class Pair:
    """
    图像对类。
    """

    def __init__(self) -> None:
        self.original: Path = Path()
        "原始文件路径"

        self.processed: Path = Path()
        "处理后文件路径"

        self.data: PicData = PicData()
        "图像数据"

    def __repr__(self) -> str:
        s: str = f"Pair(original={self.original}, processed={self.processed}, data={self.data})"
        return s

    def dump(self) -> dict[str, Any]:
        """
        将数据转换为字典。
        """
        data: dict[str, Any] = {}
        data["original"] = str(self.original)
        data["processed"] = str(self.processed)
        data.update(self.data.dump())
        return data

    def load_from_tuple(self, data: tuple) -> None:
        """
        从字典中加载数据。
        """
        self.original = Path(data[1])
        self.processed = Path(data[2])
        self.data = PicData()
        self.data.time_stamp = data[3]
        self.data.feature = json.loads(data[4]) if data[4] else None
        self.data.shooting_position = tuple(json.loads(data[5]))
        self.data.wind_dir = data[6]
        self.data.wind_scale = int(data[7])
        self.data.wind_speed = int(data[8])
        self.data.humidity = int(data[9])
        self.data.precip = float(data[10])
        self.data.pressure = int(data[11])
        self.data.vis = int(data[12])
        self.data.cloud = int(data[13])
        self.data.AS = float(data[14])
        self.data.HS = float(data[15])
        self.data.weather = data[16]
        self.data.temperature = int(data[17]) if data[17] else None


def yield_file(
    path: Path, pattern: str = "**/*.*", suffix: Optional[list[str]] = None
) -> Generator[Path, Any, None]:
    """
    遍历指定路径下的文件，并返回满足特定后缀条件的文件。
    该函数接受一个路径参数，一个模式参数和一个后缀列表参数，
    然后遍历路径下的所有文件，如果文件的后缀在给定的后缀列表中，则返回该文件。

    Parameters:
        path (Path): 需要遍历的路径。
        pattern (str, optional): 用于匹配文件的模式，默认为"**/*.*"，表示匹配所有文件。
        suffix (list, optional): 需要返回的文件的后缀列表，默认为空列表，表示返回所有类型的文件。

    Yields:
        Path: 返回满足条件的文件路径。
    """
    for file in path.glob(pattern=pattern):
        if suffix and file.suffix.lower() not in suffix:
            continue
        yield file


def yield_info(
    generator: Generator[Path, Any, None],
) -> Generator[dict[str, Any], Any, None]:
    """
    该函数用于从生成器中获取文件信息，包括时间戳、天气和温度。
    它首先定义了两个正则表达式模式来匹配时间戳，然后定义了另一个正则表达式模式来匹配天气和温度。
    对于生成器中的每个文件，它会尝试匹配这些模式，并将结果存储在字典中。

    Parameters:
        generator (Generator[Path, Any, None]): 一个生成器，其元素是Path对象，表示文件路径。

    Yields:
        dict (str, str | Path): 返回一个字典，包含以下键：
            'file': 文件。
            'time_stamp': 时间戳，如果无法匹配到时间戳，则为空字符串。
            'weather': 天气，如果无法匹配到天气，则为空字符串。
            'temperature': 温度，如果无法匹配到温度，则为空字符串。
            'img_type': 图像类型，如果无法匹配到图像类型，则为空字符串。
    """
    # 匹配时间戳
    time_case: list[tuple[str, str]] = [
        # YYYY-MM-DD-HH-MM-SS
        (r"20\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}", "%Y-%m-%d-%H-%M-%S"),
        # YYYYMMDDHHMMSS
        (r"20\d{12}", "%Y%m%d%H%M%S"),
    ]

    # 匹配天气和温度
    weather_case: list[tuple[str, str, str]] = [
        # E1: 晴23
        (r"(?:[阴晴雨雪雾]|多云)[天]?\-?\d{1,2}$", r"[阴晴雨雪雾]|多云", r"\d{1,2}$")
    ]

    # 匹配图像类型
    image_case: list[tuple[str, str]] = [
        # 红外1
        (r"^IR", "IR"),
        # 红外2
        (r"^DJI_\d+_\d+_T", "IR"),
        # 原始1
        (r"^GREY_", "NR"),
        # 原始2
        (r"^DJI_\d+_\d+_V", "NR"),
        # 原始3
        (r"^DJI_\d+_\d+_S", "NR"),
    ]

    for file in generator:
        time_stamp: str = ""
        weather_str: str = ""
        temperature_str: str = ""
        img_type: str = ""

        for pattern, time_format in time_case:
            re_result: list[str] = re.findall(pattern=pattern, string=str(file.stem))
            if not re_result:
                continue
            try:
                time_obj: datetime = datetime.strptime(re_result[0], time_format)
            except ValueError:
                continue

            time_stamp: str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            break

        for total, w_pattern, t_pattern in weather_case:
            re_result: list[str] = re.findall(pattern=total, string=str(file.stem))
            if not re_result:
                continue
            weather_str: str = re.findall(pattern=w_pattern, string=re_result[0])[0]
            temperature_str: str = re.findall(pattern=t_pattern, string=re_result[0])[0]
            break

        for pattern, itype in image_case:
            re_result: list[str] = re.findall(pattern=pattern, string=str(file.stem))
            if not re_result:
                continue
            img_type: str = itype
            break

        result: dict[str, Any] = {
            "file": file.absolute().relative_to(Path(__file__).parent),
            "time_stamp": time_stamp if time_stamp else "",
            "weather": weather_str if weather_str else "",
            "temperature": temperature_str if temperature_str else "",
            "img_type": img_type if img_type else "",
        }
        yield result


def main():
    """
    主函数。
    """

    path = Path("./images")
    old_data_file: Path = Path("ir_database.json")
    data_file: Path = Path("database.json")
    suffix: list[str] = [".jpg", ".png"]

    generator: Generator[Path, Any, None] = yield_file(path=path, suffix=suffix)

    # 获取数据集对
    pair_dict: dict[str, Pair] = {}
    for i in yield_info(generator=generator):
        time_stamp: str = i["time_stamp"]
        if not time_stamp:
            continue
        if time_stamp not in pair_dict:
            pair_dict[time_stamp] = Pair()
            pair_dict[time_stamp].data.time_stamp = time_stamp

        pair: Pair = pair_dict[time_stamp]

        if i["img_type"] == "IR":
            pair.processed = i["file"]
        else:
            pair.original = i["file"]

        if i["weather"]:
            pair.data.weather = i["weather"]

        if i["temperature"]:
            pair.data.temperature = i["temperature"]

        print(pair)

    # 验证数据集是否成对
    pd_copy = pair_dict.copy()
    for pair in pd_copy.values():
        if not pair.original or not pair.processed:
            del pair_dict[pair.data.time_stamp]
            continue
        if not pair.original.is_file() or not pair.processed.is_file():
            del pair_dict[pair.data.time_stamp]
            continue
        if not pair.original.exists() or not pair.processed.exists():
            del pair_dict[pair.data.time_stamp]
            continue
        if (
            pair.original.suffix.lower() not in suffix
            or pair.processed.suffix.lower() not in suffix
        ):
            del pair_dict[pair.data.time_stamp]
            continue
        if pair.original == Path(".") or pair.processed == Path("."):
            del pair_dict[pair.data.time_stamp]
            continue
        if pair.original == Path(".\\not_file") or pair.processed == Path(
            ".\\not_file"
        ):
            del pair_dict[pair.data.time_stamp]
            continue

    print(f"共找到{len(pair_dict)}对数据。")

    # 继承旧数据集
    with open(file=old_data_file, mode="r", encoding="utf-8") as f:
        old_data: dict[str, Any] = json.load(f)
        records: list[dict[str, Any]] = old_data.get("RECORDS", [])
        for record in records:
            _time_stamp: str = record.get("create_time", "")
            if not _time_stamp:
                continue
            time_stamp: str = _time_stamp.split(".")[0]
            if time_stamp in pair_dict:
                pair: Pair = pair_dict[time_stamp]
                _shoot_lating = record.get("shoot_latlng", '["0.0","0.0"]')
                shoot_lating: list[str] = json.loads(_shoot_lating)
                pair.data.shooting_position = (
                    float(shoot_lating[0]),
                    float(shoot_lating[1]),
                )
                temp: str = record.get("temp", "")
                pair.data.temperature = int(temp)
                pair.data.wind_dir = record.get("wind_dir", "")
                pair.data.wind_scale = int(record.get("wind_scale", 0))
                pair.data.wind_speed = int(record.get("wind_speed", 0))
                pair.data.humidity = int(record.get("humidity", 0))
                pair.data.precip = float(record.get("precip", 0.0))
                pair.data.pressure = int(record.get("pressure", 0))
                pair.data.vis = int(record.get("vis", 0))
                pair.data.cloud = int(record.get("cloud", 0))
                pair.data.AS = float(record.get("AS", 0.0))
                pair.data.HS = float(record.get("HS", 0.0))

    # 对部分数据集进行信息补充
    for pair in pair_dict.values():
        if "长大" in str(pair.original.absolute()):
            pair.data.shooting_position = (113.271431, 23.135336)
        elif "厦大" in str(pair.original.absolute()):
            pair.data.shooting_position = (118.317851, 24.609725)

    # 保存数据集
    data = {}
    data["RECORDS"] = [pair.dump() for pair in pair_dict.values()]
    with open(file=data_file, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
    _data_file: Path = Path("./database.json")
    _database_file: Path = Path("./database.db")
    convert_to_sqlite(data_file=_data_file, database_file=_database_file)
    print("Done!")
