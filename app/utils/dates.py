from datetime import datetime
from zoneinfo import ZoneInfo

SAO_PAULO = ZoneInfo('America/Sao_Paulo')


def local_now() -> datetime:
    return datetime.now(SAO_PAULO)


def local_today():
    return local_now().date()
