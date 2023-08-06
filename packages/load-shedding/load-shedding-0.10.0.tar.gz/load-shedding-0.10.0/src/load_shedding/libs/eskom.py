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
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Tuple

import certifi
import urllib3
from bs4 import BeautifulSoup


class EskomError(Exception):
    pass


class Province(Enum):
    EASTERN_CAPE = 1
    FREE_STATE = 2
    GAUTENG = 3
    KWAZULU_NATAL = 4
    LIMPOPO = 6
    MPUMALANGA = 5
    NORTH_WEST = 7
    NORTERN_CAPE = 8
    WESTERN_CAPE = 9

    def __str__(self):
        return {
            self.EASTERN_CAPE: "Eastern Cape",
            self.FREE_STATE: "Free State",
            self.GAUTENG: "Gauteng",
            self.KWAZULU_NATAL: "Kwa-Zulu Natal",
            self.LIMPOPO: "Limpopo",
            self.MPUMALANGA: "Mpumalanga",
            self.NORTH_WEST: "North West",
            self.NORTERN_CAPE: "Nortern Cape",
            self.WESTERN_CAPE: "Western Cape",
        }.get(self, "Unknown Province")


class LoadShedding:
    base_url = "https://loadshedding.eskom.co.za/LoadShedding"

    def find_suburbs(self, search_text: str, max_results: int = 10) -> List[Dict]:
        if not max_results:
            max_results = 10
        url = f"{self.base_url}/FindSuburbs?searchText={search_text}&maxResults={max_results}"
        data = _call(url)
        return json.loads(data)

    def get_municipalities(self, province: Province) -> List[Dict]:
        url = f"{self.base_url}/GetMunicipalities/?Id={province.value}"
        data = _call(url)
        return json.loads(data)

    def get_schedule(self, province: Province, suburb_id: int, stage: int) -> List[Tuple]:
        tot: int = 3252
        url = f"{self.base_url}/GetScheduleM/{suburb_id}/{stage}/{province}/{tot}"
        data = _call(url)
        return parse_schedule_data(data)

    def get_schedule_area_info(self, suburb_id: int) -> Dict:
        url = f"{self.base_url}/GetScheduleAreaInfo/?Id={suburb_id}"
        data = _call(url)
        return parse_area_info_data(data)

    def get_status(self) -> int:
        url = f"{self.base_url}/GetStatus"
        data = _call(url)
        return int(data)


def _call(url: str) -> Any:
    try:
        with urllib3.PoolManager(retries=urllib3.Retry(total=3), ca_certs=certifi.where()) as conn:
            r = conn.request('GET', url)
            if r.status != 200:
                raise urllib3.response.HTTPError(r.status)
            return r.data
    except Exception as e:
        raise EskomError(f"Eskom is unreachable. Check your connection.") from e


def parse_area_info_data(data: str) -> Dict:
    try:
        soup = BeautifulSoup(data, "html.parser")
        items = soup.find_all("div", attrs={"class": "areaInfoItem"})
        area_info = {
            "Province": {
                "Id": int(items[0].find("input", attrs={"id": "provinceId"}).get('value').strip()),
                "Name": items[0].find("input", attrs={"id": "province"}).get('value').strip(),
            },
            "Municipality": {
                "Id": int(items[1].find("input", attrs={"id": "municipalityId"}).get('value').strip()),
                "Name": items[1].find("input", attrs={"id": "municipality"}).get('value').strip(),
            },
            "Suburb": {
                "Id": int(items[2].find("input", attrs={"id": "suburbId"}).get('value').strip()),
                "Name": items[2].find("input", attrs={"id": "suburbName"}).get('value').strip(),
            },
            "Period": items[3].contents[2].strip().split("\xa0to\xa0"),
        }
    except Exception as e:
        raise EskomError(f"Unable to parse area info data.") from e
    else:
        return area_info


def parse_schedule_data(data: str) -> List[Tuple]:
    try:
        schedule = []
        soup = BeautifulSoup(data, "html.parser")
        days_soup = soup.find_all("div", attrs={"class": "scheduleDay"})

        sast = timezone(timedelta(hours=+2), 'SAST')
        now = datetime.now(sast)
        for day in days_soup:
            date_soup = day.find("div", attrs={"class": "dayMonth"})
            date_str = date_soup.get_text().strip()
            date = datetime.strptime(date_str, "%a, %d %b")
            date = date.replace(year=now.year)

            time_soup = day.find_all("a")
            for time_tag in time_soup:
                start_str, end_str = time_tag.get_text().strip().split(" - ")
                start = datetime.strptime(start_str, "%H:%M").replace(
                    year=date.year, month=date.month, day=date.day, second=0, microsecond=0, tzinfo=sast
                )
                end = datetime.strptime(end_str, "%H:%M").replace(
                    year=date.year, month=date.month, day=date.day, second=0, microsecond=0, tzinfo=sast
                )
                if end < start:
                    end = end + timedelta(days=1)
                schedule.append((start, end))
    except Exception as e:
        raise EskomError(f"Unable to parse schedule data.") from e
    else:
        return schedule
