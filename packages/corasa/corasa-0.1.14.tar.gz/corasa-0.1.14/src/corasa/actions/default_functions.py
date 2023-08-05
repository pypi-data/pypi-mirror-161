import re

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

re_iso_date = re.compile(r"^\d\d\d\d-\d\d-\d\d$")
re_iso_time = re.compile(r"^\d\d:\d\d:\d\d(\.\d\d\d\d\d\d)?$")
re_iso_datetime = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d\d\d\d\d\d)?$")


def get_datetime_dict(type, value_1=None, value_2=None):
    """Helper to create the dict structure for DateTime."""
    d = {"_type": "DateTime", "type": type}

    if type in ["datetime", "time", "date"]:
        d["value"] = value_1
    else:
        d["value"] = f"{value_1} to {value_2}"
        if value_1:
            d["from_value"] = {"type": type.split("_")[0], "value": value_1}
        if value_2:
            d["to_value"] = {"type": type.split("_")[0], "value": value_2}

    return d


def convert(value: str, type_name: str):
    """Helper to convert a value to a new type.

    Initial use case, to convert string to DateTime objects.
    """
    if type_name in ["time", "date", "datetime"]:
        return get_datetime_dict(type_name, value)

    # Otherwise, just return the value
    return value


def datetime(*args):
    """Constructor for a datetime object."""
    if len(args) == 1:
        return get_datetime_dict("datetime", args[0])
    elif len(args) == 2:
        # We're dealing with a date and a time
        date_str = args[0]
        if isinstance(date_str, dict):
            date_str = date_str["value"]

        time_str = args[1]
        if isinstance(time_str, dict):
            time_str = time_str["value"]

        return get_datetime_dict("datetime", f"{date_str}T{time_str}")

    return None


def datetime_add(val, hours=None, days=None, weeks=None, months=None, years=None):
    """Adds the specified components to a datetime."""
    if isinstance(val, str):
        dt_val = parse(val)
    elif isinstance(val, dict) and val["type"] in ["date", "datetime"]:
        dt_val = parse(val["value"])
    else:
        raise Exception(f"Unknown datetime format: {val}")

    delta = relativedelta(
        hours=hours or 0,
        days=days or 0,
        weeks=weeks or 0,
        months=months or 0,
        years=years or 0,
    )
    dt_val = dt_val + delta

    return get_datetime_dict("datetime", dt_val.isoformat())


def date_add(val, days=None, weeks=None, months=None, years=None):
    """Adds the specified components to a date."""
    result = datetime_add(val, days=days, weeks=weeks, months=months, years=years)
    return get_datetime_dict("date", result["value"][0:10])


def date(*args):
    """Constructor for a date.

    Works both with a string and a DateTime instance.
    """
    if not args:
        return None

    if isinstance(args[0], str):
        if re_iso_date.match(args[0]) or re_iso_datetime.match(args[0]):
            return get_datetime_dict("date", args[0][0:10])

    elif isinstance(args[0], dict):
        if args[0]["type"] == "datetime":
            return get_datetime_dict("date", args[0]["value"][0:10])
        elif args[0]["type"] == "date":
            return get_datetime_dict("date", args[0]["value"])

    return None


def time(*args):
    """Constructor for a time.

    Works both with a string and a DateTime instance.
    """
    if not args:
        return None

    if isinstance(args[0], str):
        if re_iso_time.match(args[0]):
            return get_datetime_dict("time", args[0])
        elif re_iso_datetime.match(args[0]):
            return get_datetime_dict("time", args[0][11:])

    elif isinstance(args[0], dict):
        if args[0]["type"] == "datetime":
            return get_datetime_dict("time", args[0]["value"][11:])

    return None


def datetime_interval(*args):
    """Constructor for a datetime_interval object"""
    if len(args) == 2:
        if (
            isinstance(args[0], dict)
            and isinstance(args[1], dict)
            and args[0]["type"] == "date"
            and args[1]["type"] == "time_interval"
        ):
            from_value = f"{args[0]['value']}T{args[1]['from_value']['value']}"
            to_value = f"{args[0]['value']}T{args[1]['to_value']['value']}"
            return get_datetime_dict("datetime_interval", from_value, to_value)

        elif (
            isinstance(args[0], dict)
            and isinstance(args[1], dict)
            and args[0]["type"] == "datetime"
            and args[1]["type"] == "datetime"
        ):
            return get_datetime_dict(
                "datetime_interval", args[0]["value"], args[1]["value"]
            )

    return None


def weekday(dt):
    res = parse(dt["value"]).weekday()
    return res


# The list of default functions available when evaluating expressions
default_functions = {
    "convert": convert,
    "date": date,
    "time": time,
    "datetime": datetime,
    "datetime_interval": datetime_interval,
    "date_add": date_add,
    "datetime_add": datetime_add,
    "weekday": weekday,
}
