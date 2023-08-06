import datetime, re

format_dates = {
    r"[0-9]{2}-[a-zA-Z]+-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}": "%d-%b-%y %H:%M:%S",
    r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}": "%Y-%m-%d %H:%M:%S",
    r"[0-9]{4}\/[0-9]{2}\/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}": "%Y/%m/%d %H:%M:%S",
    r"[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}": "%d/%m/%Y %H:%M:%S",
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+": "%H:%M:%S.%f",
    r"[0-9]{2}_[0-9]{2}_[0-9]{2}": "%d_%m_%y",
}

format_date = "%Y-%m-%d %H:%M:%S"
format_date2 = "%Y/%m/%d %H:%M:%S"
format_date3 = "%d/%m/%Y %H:%M:%S"
format_date_ws = "%H:%M:%S.%f"
format_date_4 = "%d_%m_%y"


def str_to_datetime_if_needed(date_string):
    if re.findall(r"[0-9]+-[0-9]+-[0-9]+[T\s][0-9]+:[0-9]+:[0-9]+"):
        return str_to_datetime(date_string)
    return date_string


def str_to_datetime(date_string):
    if "T" in date_string:
        date_string = date_string.replace("T", "")
    if not type(date_string) == str:
        return date_string

    format_date_selected = None
    for regex, format in format_dates.items():
        match = re.search(regex, date_string, re.IGNORECASE)
        if match is not None:
            format_date_selected = format

    if format_date_selected is None:  # TODO: delete
        if date_string[2] == "/":
            format_date_selected = format_date3
        elif date_string[4] == "/":
            format_date_selected = format_date2
        elif date_string[2] == ":" and date_string[8] == ".":
            format_date_selected = format_date_ws
        else:
            format_date_selected = format_date

    if format_date_selected is not None:
        if len(date_string) == 10:
            format_date_selected = format_date_selected.split()[0]
        output = datetime.datetime.strptime(date_string, format_date_selected)
        return output
    return date_string


def datetime_to_str(o=None, micro=False):
    if o is None:
        o = datetime.datetime.now()
    return str(o.strftime(format_date if not micro else format_date + ".%f"))


def timedelta_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = "s" if period_value > 1 else ""
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)
