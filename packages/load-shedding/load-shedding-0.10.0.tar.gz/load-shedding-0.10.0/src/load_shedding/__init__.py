from enum import Enum

from .load_shedding import (
    Area, Stage, StageError, ProviderError,
    get_areas, get_area_schedule, get_stage, get_stage_forecast, get_area_forecast
)
from .providers import Province, coct, eskom


class Provider(Enum):
    ESKOM = 1
    COCT = 2

    def __call__(self, *args, **kwargs):
        return {
            Provider.ESKOM: eskom.Eskom(),
            Provider.COCT: coct.CoCT(),
        }.get(self, None)

    def load(self):
        return {
            Provider.ESKOM: eskom.Eskom(),
            Provider.COCT: coct.CoCT(),
        }.get(self, None)

    def __str__(self):
        return {
            self.ESKOM: eskom.Eskom.name,
            self.COCT: coct.CoCT.name,
        }.get(self, "Unknown Provider")
