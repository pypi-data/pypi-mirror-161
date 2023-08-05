from dataclasses import dataclass
from datetime import datetime


@dataclass
class FilterContext:
    start_time: datetime
    end_time: datetime
