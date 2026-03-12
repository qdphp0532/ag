"""时间 / 日期类工具。"""
from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def get_current_time(timezone_name: str = "UTC") -> str:
    """获取当前日期时间，用于回答“现在几点”“今天几号”等问题。

    Args:
        timezone_name: 时区名，如 UTC、Asia/Shanghai，默认 UTC
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = timezone.utc
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")
