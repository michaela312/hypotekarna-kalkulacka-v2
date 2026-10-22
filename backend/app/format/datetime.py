"""B7a – formát dátumu a času uloženia (NOVÉ vo V2).

Implementuje FR-11: čas v UTC → `15. 10. 2026 14:05` v pásme Europe/Bratislava (letný aj zimný čas).
Na Windows potrebuje balík tzdata (R-P-03).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo('Europe/Bratislava')


def format_datetime(utc: datetime) -> str:
    if utc.tzinfo is None:
        raise ValueError('Čas musí mať časové pásmo (UTC).')   # kontrakt (TQ-01)
    local = utc.astimezone(TIMEZONE)
    return f'{local.day}. {local.month}. {local.year} {local.hour:02d}:{local.minute:02d}'
