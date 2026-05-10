from __future__ import annotations

import re
from datetime import date, datetime
from datetime import time as dt_time

WEEKDAY_MAP = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


class TimeParser:
    """Parses and evaluates time range expressions for inspection rules.

    Supports combining date, weekday, and time ranges in a single string.
    Examples:
        ``2026-10-01~2026-10-07 Mon-Fri 09:00-18:00``
        ``Mon-Fri 09:00-18:00``
        ``09:00-18:00``
        ``22:00-02:00`` (cross-day)

    解析并评估时间范围表达式，用于巡检规则。
    支持日期、星期和时间范围的组合。
    例如：
        ``2026-10-01~2026-10-07 Mon-Fri 09:00-18:00``
        ``Mon-Fri 09:00-18:00``
        ``09:00-18:00``
        ``22:00-02:00`` (跨天时间范围)
    """

    @staticmethod
    def is_in_range(time_range_str: str) -> bool:
        """Check if current datetime is within the specified time range.

        判断当前时间是否落在给定范围内。

        An empty or whitespace-only string means always active.
        空字符串或纯空白字符串表示始终生效。
        """
        if not time_range_str or not time_range_str.strip():
            return True

        parts = time_range_str.strip().split()
        now = datetime.now()

        date_ok = True
        weekday_ok = True
        time_ok = True

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if TimeParser._looks_like_date(part):
                date_ok = TimeParser._parse_date_range(part, now)
            elif TimeParser._looks_like_weekday(part):
                weekday_ok = TimeParser._parse_weekday_range(part, now)
            elif TimeParser._looks_like_time(part):
                time_ok = TimeParser._parse_time_range(part, now)

        return date_ok and weekday_ok and time_ok

    @staticmethod
    def _looks_like_date(part: str) -> bool:
        return bool(re.match(r"^\d{2,4}-\d{1,2}", part))

    @staticmethod
    def _looks_like_weekday(part: str) -> bool:
        lower = part.lower()
        for abbr in WEEKDAY_MAP:
            if abbr in lower:
                return True
        return False

    @staticmethod
    def _looks_like_time(part: str) -> bool:
        return bool(re.match(r"^\d{1,2}:\d{2}-\d{1,2}:\d{2}$", part))

    @staticmethod
    def _parse_date_range(part: str, now: datetime) -> bool:
        """Parse a date or date range expression.

        解析单日期或日期区间表达式。
        """
        if "~" in part:
            start_str, end_str = part.split("~", 1)
            start = TimeParser._resolve_date(start_str.strip(), now)
            end = TimeParser._resolve_date(end_str.strip(), now)
            if start is None or end is None:
                return True
            return start <= now.date() <= end
        else:
            target = TimeParser._resolve_date(part.strip(), now)
            if target is None:
                return True
            return now.date() == target

    @staticmethod
    def _resolve_date(date_str: str, now: datetime) -> date | None:
        try:
            parts = date_str.split("-")
            if len(parts) == 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                if year < 100:
                    year = now.year
                return now.replace(year=year, month=month, day=day).date()
            elif len(parts) == 2:
                month = int(parts[0])
                day = int(parts[1])
                return now.replace(month=month, day=day).date()
            elif len(parts) == 1:
                day = int(parts[0])
                return now.replace(day=day).date()
        except (ValueError, OverflowError):
            return None
        return None

    @staticmethod
    def _parse_weekday_range(part: str, now: datetime) -> bool:
        """Parse a weekday expression.

        解析星期表达式。
        """
        lower = part.lower()

        if "," in lower:
            days = [d.strip() for d in lower.split(",")]
            target_weekdays = set()
            for d in days:
                if d in WEEKDAY_MAP:
                    target_weekdays.add(WEEKDAY_MAP[d])
            return now.weekday() in target_weekdays

        if "-" in lower:
            start_str, end_str = lower.split("-", 1)
            start_wd = WEEKDAY_MAP.get(start_str.strip())
            end_wd = WEEKDAY_MAP.get(end_str.strip())
            if start_wd is None or end_wd is None:
                return True
            if start_wd <= end_wd:
                return start_wd <= now.weekday() <= end_wd
            else:
                return now.weekday() >= start_wd or now.weekday() <= end_wd

        single = lower.strip()
        if single in WEEKDAY_MAP:
            return now.weekday() == WEEKDAY_MAP[single]

        return True

    @staticmethod
    def _parse_time_range(part: str, now: datetime) -> bool:
        """Parse a time range expression, including cross-day ranges.

        解析时间范围表达式，支持跨天区间。
        """
        match = re.match(r"^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$", part)
        if not match:
            return True

        sh, sm, eh, em = (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
        )
        try:
            start_time = dt_time(sh, sm)
            end_time = dt_time(eh, em)
        except ValueError:
            return True

        current_time = now.time()

        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            return current_time >= start_time or current_time <= end_time
