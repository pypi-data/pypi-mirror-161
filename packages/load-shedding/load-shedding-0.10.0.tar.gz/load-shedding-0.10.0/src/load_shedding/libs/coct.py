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
import json
import logging
from datetime import datetime, time, timedelta, timezone
from enum import Enum
from typing import List, Tuple, Any

import certifi
import urllib3

_LOGGER = logging.getLogger(__name__)

MAX_MONTH_DAY = 31

DAY_AREA_EXTRA_INCREMENTS = [5, 9]
DAY_AREA_EXTR_INCREMENTS_STAGE_LOWER = [13]

STAGE_STARTING_AREAS = {
    1: 1,
    2: 9,
    3: 13,
    4: 5,
    5: 2,
    6: 10,
    7: 14,
    8: 6
}

TIME_SLOT_HOURS = 2
TIME_SLOT_MINUTES = 30

SAST = timezone(timedelta(hours=+2), 'SAST')


class CoCTError(Exception):
    pass


class Area(Enum):
    AREA_1 = 1
    AREA_2 = 2
    AREA_3 = 3
    AREA_4 = 4
    AREA_5 = 5
    AREA_6 = 6
    AREA_7 = 7
    AREA_8 = 8
    AREA_9 = 9
    AREA_10 = 10
    AREA_11 = 11
    AREA_12 = 12
    AREA_13 = 13
    AREA_14 = 14
    AREA_15 = 15
    AREA_16 = 16

    def __str__(self):
        return {
            self.AREA_1: "Area 1",
            self.AREA_2: "Area 2",
            self.AREA_3: "Area 3",
            self.AREA_4: "Area 4",
            self.AREA_5: "Area 5",
            self.AREA_6: "Area 6",
            self.AREA_7: "Area 7",
            self.AREA_8: "Area 8",
            self.AREA_9: "Area 9",
            self.AREA_10: "Area 10",
            self.AREA_11: "Area 11",
            self.AREA_12: "Area 12",
            self.AREA_13: "Area 13",
            self.AREA_14: "Area 14",
            self.AREA_15: "Area 15",
            self.AREA_16: "Area 16",
        }.get(self, "Unknown Area")


class Stage(Enum):
    NO_LOAD_SHEDDING = 0
    STAGE_1 = 1
    STAGE_2 = 2
    STAGE_3 = 3
    STAGE_4 = 4
    STAGE_5 = 5
    STAGE_6 = 6
    STAGE_7 = 7
    STAGE_8 = 8


SLOT = datetime.now().replace(year=1, month=1, day=1, second=0, microsecond=0)
TIMESLOTS: List[List] = [
    (SLOT.replace(hour=0, minute=0), SLOT.replace(hour=2, minute=30)),
    (SLOT.replace(hour=2, minute=0), SLOT.replace(hour=4, minute=30)),
    (SLOT.replace(hour=4, minute=0), SLOT.replace(hour=6, minute=30)),
    (SLOT.replace(hour=6, minute=0), SLOT.replace(hour=8, minute=30)),
    (SLOT.replace(hour=8, minute=0), SLOT.replace(hour=10, minute=30)),
    (SLOT.replace(hour=10, minute=0), SLOT.replace(hour=12, minute=30)),
    (SLOT.replace(hour=12, minute=0), SLOT.replace(hour=14, minute=30)),
    (SLOT.replace(hour=14, minute=0), SLOT.replace(hour=16, minute=30)),
    (SLOT.replace(hour=16, minute=0), SLOT.replace(hour=18, minute=30)),
    (SLOT.replace(hour=18, minute=0), SLOT.replace(hour=20, minute=30)),
    (SLOT.replace(hour=20, minute=0), SLOT.replace(hour=22, minute=30)),
    (SLOT.replace(hour=22, minute=0), SLOT.replace(hour=0, minute=30)),
]


def get_schedule(area: Area, stage: Stage, days=30):
    """ Returns a schedule for the given area, stage and number of days."""
    schedule: List[Tuple] = []
    today = datetime.now(tz=SAST).replace(second=0, microsecond=0)
    day = today

    while day < today + timedelta(days=days):
        timeslots = get_time_slots_by_area_code(stage.value, day.day, area.value)

        for ts in timeslots:
            start = ts[0].replace(year=day.year, month=day.month, day=day.day, tzinfo=SAST)
            end = ts[1].replace(year=day.year, month=day.month, day=day.day, tzinfo=SAST)
            if end < start:
                end = end + timedelta(days=1)
            schedule.append((start, end))
        day = day + timedelta(days=1)
    return schedule


def get_area_codes_by_time_slot(stage, day, time_slot):
    day = _clip_day_to_group(day)
    area_code_acc = _get_area_code_accumulation_day_start(stage, day) + time_slot
    if stage > 4:
        area_code_acc += 1
    area_code = _nomalize_area_code(stage, area_code_acc)
    area_codes = [area_code]

    if stage == 4 and time_slot == 4 and day == 15:
        area_codes = []

    if stage > 1:
        area_codes = area_codes + get_area_codes_by_time_slot(stage - 1, day, time_slot)

    return area_codes


def get_time_slots_by_area_code(stage, day, area):
    time_slots = []
    for i in range(len(TIMESLOTS)):
        areas = get_area_codes_by_time_slot(stage, day, i + 1)
        if area in areas:
            time_slots.append(TIMESLOTS[i])
            continue

    return time_slots


def get_next_time_slot(stage: int, area_code: int) -> Tuple:
    # result = {"slot": None, "day": None, "date": None}

    if stage < 1 or stage > len(Stage):
        logging.debug("get_next_time_slot() stage out of bounds")
        return ()

    if area_code < 1 or area_code > len(Area):
        logging.debug("get_next_time_slot() area_code out of bounds")
        return ()

    d = datetime.now()  # + timedelta(hours=2)
    from_hour = d.hour
    from_day = d.day

    slot = None
    day = from_day
    day_accum = 0

    while not slot:
        slot = get_next_time_slot_in_day(
            stage, day, area_code, from_hour if day == from_day else -1
        )

        if not slot:
            if day >= MAX_MONTH_DAY:
                day = 1
            else:
                day += 1

            day_accum += 1

    return TIMESLOTS[slot - 1]

    new_date = datetime(d.year, d.month, d.day, get_time_slot_hour(slot), 0, 0)
    new_date = new_date + timedelta(days=day_accum)

    result["slot"] = slot
    result["day"] = day
    result["date"] = new_date

    return result


def get_time_slot_hour(slot):
    return (slot - 1) * TIME_SLOT_HOURS


def _get_timeslot_from_hour(hour):
    is_odd_hour = (hour % TIME_SLOT_HOURS) != 0

    time_slot = hour
    if is_odd_hour:
        time_slot -= 1

    return time_slot // TIME_SLOT_HOURS + 1


def _clip_day_to_group(day):
    if day > len(Area):
        day -= len(Area)
    return day


def _get_area_code_accumulation_day_start(stage, day):
    if day <= 1:
        return 0

    day_before = day - 1
    area_code_acc = day_before * len(TIMESLOTS)

    for i in DAY_AREA_EXTRA_INCREMENTS:
        if day >= i:
            area_code_acc += 1

    if stage <= 4:
        for i in DAY_AREA_EXTR_INCREMENTS_STAGE_LOWER:
            if day >= i:
                area_code_acc += 1

    return area_code_acc


def _nomalize_area_code(stage, area_code_acc):
    area_code = area_code_acc % len(Area)
    area_code += STAGE_STARTING_AREAS[stage] - 1
    if area_code > len(Area):
        area_code -= len(Area)

    return area_code


def get_next_time_slot_in_day(stage, day, area_code, from_hour=-1):
    slots = get_time_slots_by_area_code(stage, day, area_code)

    for slot in slots:
        slot_hour = get_time_slot_hour(slot)

        if from_hour == -1 or slot_hour > from_hour:
            return slot

    return None


def get_info():
    url = "https://d42sspn7yra3u.cloudfront.net"
    data = _call(url)
    return parse_info(data)


def _call(url: str) -> Any:
    try:
        with urllib3.PoolManager(retries=urllib3.Retry(total=3), ca_certs=certifi.where()) as conn:
            r = conn.request('GET', url)
            if r.status != 200:
                raise urllib3.response.HTTPError(r.status)
            return r.data
    except Exception as e:
        raise CoCTError(f"CoCT is unreachable. Check your connection.") from e


def parse_info(data: str):
    try:
        info = []
        for i in json.loads(data):
            info.append({
                "current_stage": int(i.get("currentStage")),
                "start_time": datetime.strptime(i.get("nextStageStartTime"), "%Y-%m-%dT%H:%M").replace(tzinfo=SAST),
                "next_stage": int(i.get("nextStage")),
                "next_stage_start_time": datetime.strptime(i.get("nextStageStartTime"), "%Y-%m-%dT%H:%M").replace(tzinfo=SAST)
            })
    except Exception as err:
        raise CoCTError from err
    else:
        return info