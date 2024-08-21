from datetime import datetime


def validate_date(date_string, start_date=None, end_date=None) -> bool | str:
    try:
        date_obj = datetime.strptime(date_string, "%d.%m.%Y")
        if datetime.strptime(date_string, "%d.%m.%Y").date() < datetime.now().date():
            return "old_date_error"
        if (
            start_date
            and datetime.strptime(start_date, "%d.%m.%Y")
            > datetime.strptime(date_string, "%d.%m.%Y")
        ) or (
            end_date
            and datetime.strptime(end_date, "%d.%m.%Y")
            < datetime.strptime(date_string, "%d.%m.%Y")
        ):
            return "timeline_error"
        return date_obj.strftime("%d.%m.%Y") == date_string
    except ValueError:
        return False
