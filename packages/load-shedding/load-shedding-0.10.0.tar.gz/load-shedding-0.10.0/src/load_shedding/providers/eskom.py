#      A python library for getting Load Shedding schedules.
#      Copyright (C) 2021  Werner Pieterson
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from datetime import timezone
from typing import List, Tuple

from load_shedding.libs import eskom, citypower
from load_shedding.providers import dict_list_to_obj_list, ProviderError, to_utc
from load_shedding.providers import Area, Province, Stage, Provider


class Area(Area):
    def __init__(self, /, **kwargs) -> object:
        self.id: int = int(kwargs.get("Id", kwargs.get("id", 0)))
        self.name: str = kwargs.get("Name", kwargs.get("name", ""))
        self.municipality: str = kwargs.get("Municipality", kwargs.get("MunicipalityName", kwargs.get("municipality", "")))
        self.province: Province = Province.from_name(kwargs.get("ProvinceName", ""))
        self.total = kwargs.get("Total")


class Eskom(Provider):
    name = "Eskom Direct"

    def __init__(self) -> object:
        self.api = eskom.LoadShedding()

    def get_areas(self, search_text: str = None, max_results: int = None) -> List[Area]:
        try:
            areas = self.api.find_suburbs(search_text, max_results)
        except Exception as e:
            raise ProviderError(e)
        else:
            areas = dict_list_to_obj_list(areas, Area)
            return filter_empty_areas(areas)

    def get_area_schedule(self, area: Area, stage: Stage) -> List[Tuple]:
        try:
            area_schedule = self.api.get_schedule(province=area.province.value, suburb_id=area.id, stage=stage.value)
        except Exception as e:
            raise ProviderError(e)
        else:
            area_schedule = to_utc(area_schedule)
            return area_schedule

    def get_stage(self) -> Stage:
        try:
            status = self.api.get_status()
        except Exception as e:
            raise ProviderError(e)
        else:
            return stage_from_status(status)

    def get_stage_forecast(self) -> List:
        """ Get Stage forecast from City Power."""
        try:
            stage_forecast = citypower.get_stage_forecast()

            for i in range(len(stage_forecast)):
                stage_forecast[i]["stage"] = Stage(stage_forecast[i].get("stage"))
                stage_forecast[i]["start_time"] = stage_forecast[i]["start_time"].astimezone(timezone.utc)
                stage_forecast[i]["end_time"] = stage_forecast[i]["end_time"].astimezone(timezone.utc)
        except Exception as e:
            raise ProviderError(e)
        else:
            return stage_forecast


def stage_from_status(status: int) -> Stage:
    return {
        1: Stage.NO_LOAD_SHEDDING,
        2: Stage.STAGE_1,
        3: Stage.STAGE_2,
        4: Stage.STAGE_3,
        5: Stage.STAGE_4,
        6: Stage.STAGE_5,
        7: Stage.STAGE_6,
        8: Stage.STAGE_7,
        9: Stage.STAGE_8,
    }.get(status, Stage.UNKNOWN)


def filter_empty_areas(suburbs: List[Area]) -> List[Area]:
    filtered: List[Area] = []
    for area in suburbs:
        if hasattr(area, "total") and not area.total:
            continue
        filtered.append(area)
    return filtered
