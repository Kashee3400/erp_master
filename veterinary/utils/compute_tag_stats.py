from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple, Optional


def get_period_range(
    date_str: Optional[str], period: str
) -> Tuple[datetime, datetime, datetime, datetime, datetime]:
    input_date = (
        datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    )

    if period == "day":
        start = input_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        prev_start = start - timedelta(days=1)
        prev_end = start

    elif period == "week":
        start = input_date - timedelta(days=input_date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        prev_start = start - timedelta(days=7)
        prev_end = start

    elif period == "month":
        start = input_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start + relativedelta(months=1)
        prev_start = start - relativedelta(months=1)
        prev_end = start

    elif period == "year":
        start = input_date.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = start + relativedelta(years=1)
        prev_start = start - relativedelta(years=1)
        prev_end = start

    else:
        return None, None, None, None, None

    return start, end, prev_start, prev_end, input_date
