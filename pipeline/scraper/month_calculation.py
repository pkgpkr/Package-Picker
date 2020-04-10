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
                         29 if year % 4 == 0 and not year % 400 == 0 else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date.replace(day=day, month=month, year=year)


def get_monthly_search_str(start_date):
    """
    Get a month-specifying date string for GitHub v4 API
    """

    end_date = month_delta(start_date, 1)
    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    return "created:" + end_date_str + ".." + start_date_str
