"""时间 / 日期类工具。"""
from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def get_current_time(timezone_name: str = "UTC") -> str:
    """获取当前日期时间。仅当用户问题依赖「现在」的日期/时刻时调用。

    Args:
        timezone_name: 时区名，如 Asia/Shanghai、UTC；中国用户优先 Asia/Shanghai
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = timezone.utc
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")
