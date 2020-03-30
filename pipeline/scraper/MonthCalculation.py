def monthDelta(date, delta):
    m, y = (date.month - delta) % 12, date.year + ((date.month) - delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def getMonthlySearchStr(startDate):
    endDate = monthDelta(startDate, 1)
    endDateStr = endDate.strftime("%Y-%m-%d")
    startDateStr = startDate.strftime("%Y-%m-%d")
    return "created:" + endDateStr + ".." + startDateStr
