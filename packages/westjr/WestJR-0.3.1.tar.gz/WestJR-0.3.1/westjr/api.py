from __future__ import annotations

from typing import cast

import requests
from requests import RequestException

from .const import AREAS, LINES, STATIONS, STOP_TRAINS
from .response_types import (
    AreaMaster,
    ResponseDict,
    Stations,
    TrainInfo,
    TrainMonitorInfo,
    TrainPos,
    TrainsItem,
)


class WestJR:
    def __init__(self, line: str | None = None, area: str | None = None) -> None:
        self.uri_suffix = "https://www.train-guide.westjr.co.jp/api/v3/"
        self.line = line
        self.area = area
        self.areas = AREAS
        self.lines = LINES

    def _request(self, endpoint: str, method: str = "GET") -> ResponseDict | None:
        uri = f"{self.uri_suffix}{endpoint}.json"

        if method == "GET":
            res = requests.get(url=uri)
            try:
                res.raise_for_status()
            except RequestException as e:
                print(e)
                raise e
            res_dict = res.json()
            # print(f"[{endpoint}, {uri}]\n{res_dict}", file=open(".log", "a"))
            return cast(ResponseDict, res_dict)
        else:
            return None

    def get_lines(self, area: str | None = None) -> AreaMaster:
        """
        広域エリアに属する路線一覧を取得して返す．
        該当API例: https://www.train-guide.westjr.co.jp/api/v3/area_kinki_master.json
        :param area: [必須] 広域エリア名(ex. kinki)
        :return: dict
        """
        _area = area if area else self.area
        if _area is None:
            raise ValueError("Need to set the area name.")
        endpoint = f"area_{_area}_master"

        res = self._request(endpoint=endpoint)
        if res is None:
            raise ValueError("Response is empty.")

        return cast(AreaMaster, res)

    def get_stations(self, line: str | None = None) -> Stations:
        """
        路線に所属している駅名一覧を取得して返す．
        :param line: [必須] 路線名(ex. kobesanyo)
        :return: dict
        """
        _line = line if line is not None else self.line
        if _line is None:
            raise ValueError("Need to set the line name.")
        endpoint = f"{_line}_st"

        res = self._request(endpoint=endpoint)
        if res is None:
            raise ValueError("Response is empty.")

        return cast(Stations, res)

    def get_trains(self, line: str | None = None) -> TrainPos:
        """
        列車走行位置を取得して返す．
        :param line: [必須] 路線名(ex. kobesanyo)
        :return: dict
        """
        _line = line if line is not None else self.line
        if _line is None:
            raise ValueError("Need to set the line name.")
        res = self._request(_line)
        if res is None:
            raise ValueError("Response is empty.")

        return cast(TrainPos, res)

    def get_traffic_info(self, area: str | None = None) -> TrainInfo:
        """
        路線の交通情報を取得して返す．問題が発生しているときのみ情報が載る．
        :param area: [必須] 広域エリア名(ex. kinki)
        :return: dict
        """
        _area = area if area else self.area
        if _area is None:
            raise ValueError("Need to set the area name.")
        endpoint = f"area_{_area}_trafficinfo"
        res = self._request(endpoint=endpoint)
        if res is None:
            raise ValueError("Response is empty.")

        return cast(TrainInfo, res)

    def convert_stopTrains(self, stopTrains: list[int] | None = None) -> list[str]:
        """
        駅一覧にある停車種別ID(int, 0~10)の配列を実際の停車種別名の配列に変換する．
        :param stopTrains: list[int]
        :return: list[str]
        """
        if stopTrains is not None:
            return [STOP_TRAINS[i] for i in stopTrains]
        else:
            return []

    def convert_pos(
        self, train: TrainsItem, line: str | None = None
    ) -> tuple[str | None, str | None]:
        """
        ID_ID を (前駅名称, 次駅名称) に変換する．
        停車中の場合 prev_st_name に駅名が入り，next_st_name は None となる．
        :param train: 列車オブジェクト
        :param line: 路線ID
        :return: (前駅名称, 次駅名称)
        """
        prev_st_id, next_st_id, *_ = train["pos"].split("_")

        prev_st_name, next_st_name = None, None

        _line = line if line is not None else self.line
        if _line is None:
            raise ValueError("Need to set the line name.")
        if _line not in STATIONS:
            raise ValueError(f"Invalid line name: {_line}")

        _station = STATIONS[_line]
        _direction = train["direction"]
        if _direction == 0:  # 上り
            if next_st_id == "####":
                prev_st_name = _station.get(prev_st_id)
                next_st_name = None
            else:
                prev_st_name = _station.get(next_st_id)
                next_st_name = _station.get(prev_st_id)

        elif _direction == 1:  # 下り
            prev_st_name = _station.get(prev_st_id)
            if next_st_id == "####":
                next_st_name = None
            else:
                next_st_name = _station.get(next_st_id)
        else:
            raise ValueError(f"invalid direction: {_direction}")
        return prev_st_name, next_st_name

    def get_train_monitor_info(self) -> TrainMonitorInfo:
        endpoint = "trainmonitorinfo"
        res = self._request(endpoint=endpoint)
        if res is None:
            raise ValueError("Response is empty")
        return cast(TrainMonitorInfo, res)
