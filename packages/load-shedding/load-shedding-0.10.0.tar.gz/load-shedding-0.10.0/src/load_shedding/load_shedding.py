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

import errno
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from json import JSONDecodeError
from typing import Any, Dict, Final, List, Tuple

from load_shedding.providers import (
    Area, Provider, ProviderError, Stage, StageError, datetime_to_isoformat, isoformat_to_datetime,
    citypower
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CACHE_TTL: Final = 86400  # 24 hours
MAX_FORECAST_DAYS: int = 7


class LoadSheddingError(Exception):
    pass


def get_areas(provider: Provider, search_text: str = None, max_results: int = None) -> List[Any]:
    try:
        areas = provider.get_areas(search_text, max_results)
    except ProviderError as e:
        raise ProviderError(f"Unable to get areas from {provider.name}.") from e
    else:
        return areas


def get_stage(provider: Provider) -> Stage:
    try:
        stage = provider.get_stage()
    except Exception as e:
        raise ProviderError(f"Unable to get stage from {provider.name}.") from e
    return stage


def get_stage_forecast(provider: Provider) -> List[Dict]:
    try:
        if not provider:
            provider = citypower.CityPower()
        stage_forecast = provider.get_stage_forecast()
    except Exception as e:
        raise ProviderError(f"Unable to get stage forecast from {provider.name}.") from e
    else:
        return stage_forecast


def get_area_forecast(area_schedule: List, planned: dict, now: datetime = datetime.now(timezone.utc)) -> List:
    area_forecast = []
    planned_start, planned_end = planned.get("start_time"), planned.get("end_time")

    for schedule in area_schedule:
        area_start, area_end = schedule[0], schedule[1]

        if area_start > now + timedelta(days=MAX_FORECAST_DAYS):
            continue

        if area_start < now:
            continue

        if area_start >= planned_end:
            continue
        if area_end <= planned_start:
            continue

        # Clip schedules that overlap forecast start_time and end_time
        if area_start <= planned_start and area_end <= planned_end:
            area_start = planned_start
        if area_start >= planned_start and area_end >= planned_end:
            area_end = planned_end

        if area_start == area_end:
            continue

        # if planned_start <= area_start <= planned_end and planned_start <= area_end <= planned_end:
        area_forecast.append({
            "stage": planned.get("stage"),
            "start_time": area_start.astimezone(now.tzinfo),
            "end_time": area_end.astimezone(now.tzinfo),
        })

    return area_forecast


def get_area_schedule(provider: Provider, area: Area, stage: Stage = None, cached: bool = True,
                      now=datetime.now(timezone.utc)) -> List[Tuple]:
    try:
        os.makedirs('.cache')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise LoadSheddingError(f"Unable to make cache dir.") from e

    if stage in [None]:
        stage = get_stage(provider)

    if stage in [Stage.UNKNOWN, Stage.NO_LOAD_SHEDDING]:
        raise StageError(f"{stage}")

    cached_schedules = {}
    cached_schedule = []

    cache_file = f".cache/{area.province.value}_{area.id}.json"
    try:
        with open(cache_file, "r") as cache:
            for k, v in json.loads(cache.read()).items():
                cached_schedules[Stage(int(k)).value] = v

            cached_schedule = cached_schedules.get(stage.value, {})

        if cached and cached_schedule:
            updated_at = datetime.fromisoformat(cached_schedule.get("updated_at", None))

            cache_age = (now - updated_at)
            if cache_age.total_seconds() < CACHE_TTL:
                schedule = cached_schedule.get("schedule", {})
                schedule = isoformat_to_datetime(schedule)
                return schedule
    except (AttributeError, FileNotFoundError, IndexError, JSONDecodeError, ValueError) as e:
        logging.debug(f"Unable to get schedule from cache. %s", e, exc_info=True)

    try:
        schedule = provider.get_area_schedule(area=area, stage=stage)
    except Exception as e:
        if cached_schedule:
            return cached_schedule  # best effort
        raise ProviderError(f"Unable to get schedule from {provider.name}.") from e
    else:
        with open(cache_file, "w") as cache:
            cached_schedules[stage.value] = {
                "updated_at": str(now),
                "schedule": datetime_to_isoformat(schedule),
            }
            cache.write(json.dumps(cached_schedules))
        return schedule


def list_to_dict(schedule: list, now = datetime.now(timezone.utc)) -> Dict:
    schedule_dict = {}
    for item in schedule:
        start = item[0]
        end = item[1]

    schedule_dict[start.strftime("%Y-%m-%d")] = (
        start.replace(second=now.second).strftime("%H:%M"),
        end.replace(second=now.second).strftime("%H:%M"),
    )
    return schedule_dict


def dict_list_to_obj_list(data: List[Dict], T: Any) -> Any:
    objs: List = []
    for d in data:
        s = T(**d)
        objs.append(s)
    return objs
