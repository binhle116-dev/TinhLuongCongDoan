import datetime as dt


def current_period(request):
    today = dt.date.today()
    return {"current_year": today.year, "current_month": today.month}
