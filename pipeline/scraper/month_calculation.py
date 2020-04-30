"""
Compute month-long time slices for use in GitHub scraping
"""

def month_delta(date, delta):
    """
    Get the date string corresponding with the given offset from the given date
    """

    month, year = (date.month - delta) % 12, date.year + ((date.month) - delta - 1) // 12
    if not month:
        month = 12
    day = min(date.day, [31,
                         29 if year % 4 == 0 and (not year % 100 == 0 or year % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date.replace(day=day, month=month, year=year)
