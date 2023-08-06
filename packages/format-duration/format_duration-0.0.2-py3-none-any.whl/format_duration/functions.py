from datetime import timedelta

from format_duration.src.format_duration.enums import DurationLimit


def format_duration(duration: timedelta, abbreviated: bool = False, limit: DurationLimit = None) -> str:
    """
    Format a duration in a human readable format.
    """
    years_count = duration.days // 365
    months_count = duration.days // 30
    days_count = duration.days
    hours_count = duration.seconds // 3600
    minutes_count = duration.seconds // 60 % 60
    seconds_count = duration.seconds % 60

    if limit.value >= DurationLimit.YEAR.value:
        years = f"{years_count} {'years' if not abbreviated else 'yrs'}"
    else:
        years = ''
    if limit.value >= DurationLimit.MONTH.value:
        months = f"{months_count % 12 if years_count else months_count} {'months' if not abbreviated else 'mo'}"
    else:
        months = ''
    if limit.value >= DurationLimit.DAY.value:
        days = f"{days_count % 30 if months_count else days_count} {'days' if not abbreviated else 'd'}"
    else:
        days = ''
    if limit.value >= DurationLimit.HOUR.value:
        hours = f"{hours_count} {'hours' if not abbreviated else 'h'}"
    else:
        hours = ''
    if limit.value >= DurationLimit.MINUTE.value:
        minutes = f"{minutes_count} {'minutes' if not abbreviated else 'm'}"
    else:
        minutes = ''
    if limit.value == DurationLimit.SECOND.value:
        seconds = f"{seconds_count} {'seconds' if not abbreviated else 's'}"
    else:
        seconds = ''

    if years_count > 0:
        return f'{years} {months} {days} {hours} {minutes} {seconds}'
    elif days_count > 30:
        return f'{months} {days} {hours} {minutes} {seconds}'
    elif days_count > 0:
        return f'{days}, {hours}, {minutes} {seconds}'
    elif hours_count > 0:
        return f'{hours}, {minutes} {seconds}'
    elif minutes_count > 0:
        return f'{minutes} {seconds}'
    else:
        return f'{seconds}'
