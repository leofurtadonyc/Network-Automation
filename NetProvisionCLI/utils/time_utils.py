import datetime
from typing import Optional

def parse_time_from_filename(filename: str) -> Optional[datetime.datetime]:
    try:
        parts = filename.split('_')
        date_part = parts[-2]
        time_part = parts[-1].split('.')[0]
        return datetime.datetime.strptime(f"{date_part}_{time_part}", '%Y%m%d_%H%M%S')
    except ValueError:
        return None
