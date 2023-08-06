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

import bs4
import certifi
import urllib3
from bs4 import BeautifulSoup, Tag


SAST = timezone(timedelta(hours=+2), 'SAST')


class CityPowerError(Exception):
    pass


base_url = "https://www.citypower.co.za"


def get_stage_forecast() -> Dict:
    url = f"{base_url}/customers/Pages/Load_Shedding_Downloads.aspx"
    data = _call(url)
    return parse_stage_forecast(data)


def _call(url: str) -> Any:
    try:
        with urllib3.PoolManager(retries=urllib3.Retry(total=3), ca_certs=certifi.where()) as conn:
            r = conn.request('GET', url)
            if r.status != 200:
                raise urllib3.response.HTTPError(r.status)
            return r.data
    except Exception as e:
        raise CityPowerError(f"CityPower is unreachable. Check your connection.") from e


def parse_stage_forecast(data: str) -> Dict:
    try:
        soup = BeautifulSoup(data, "html.parser")

        table_soup = soup.find("strong", text="Date").find_parent("table").find_next_sibling("table")
        forecast = []
        rows_soup = table_soup.find_all("tr")
        for row in rows_soup:
            cols_soup = row.find_all("td")
            next_stage = {}
            stage_date = None
            for c in range(len(cols_soup)):
                text = cols_soup[c].text
                text = text.strip().replace("\n", "").replace("\u200b", "")
                if not text:
                    break
                if c == 0:
                    text = text.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
                    stage_date = datetime.strptime(text, "%d %B %Y")
                if c == 2:
                    text = text.replace("24:", "00:")
                    start_time = datetime.strptime(text, "%H:%M")
                    start_time = start_time.replace(year=stage_date.year, month=stage_date.month, day=stage_date.day, tzinfo=SAST)
                    next_stage["start_time"] = start_time
                if c == 3:
                    text = text.replace("24:", "00:")
                    end_time = datetime.strptime(text, "%H:%M")
                    end_time = end_time.replace(year=stage_date.year, month=stage_date.month, day=stage_date.day, tzinfo=SAST)
                    if end_time < start_time:
                        end_time = end_time + timedelta(days=1)
                    if end_time < datetime.now(tz=SAST):
                        next_stage = {}
                        break
                    next_stage["end_time"] = end_time
                if c == 4:
                    try:
                        next_stage["stage"] = int(text)
                    except ValueError as err:
                        next_stage["stage"] = 0
            if next_stage:
                forecast.append(next_stage)
    except Exception as e:
        raise CityPowerError(f"Unable to parse HTML.") from e
    else:
        return forecast

