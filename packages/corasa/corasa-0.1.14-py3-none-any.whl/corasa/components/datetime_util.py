import json
import logging
import re
from datetime import datetime
from typing import Optional, List

from dateutil import parser
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from ..actions.default_functions import get_datetime_dict

logger = logging.getLogger(__name__)

re_iso_date = re.compile(r"^\d\d\d\d-\d\d-\d\d$")
re_iso_time = re.compile(r"^\d\d:\d\d:\d\d(?:\.\d\d\d\d\d\d)?$")
re_iso_datetime = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d\d\d\d\d\d)?$")

DATE_WORDS = [
    "now",
    # relative days
    "today",
    "tomorrow",
    "yesterday",
    # weekdays
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    # months
    "january",
    "jan",
    "february",
    "feb",
    "march",
    "mar",
    "april",
    "apr",
    "may",
    "june",
    "jun",
    "july",
    "jul",
    "august",
    "aug",
    "september",
    "sep",
    "october",
    "oct",
    "november",
    "nov",
    "december",
    "dec",
    # periods
    "week",
    "month",
]
re_date_mention = re.compile(
    "|".join([rf"\b{word}\b" for word in DATE_WORDS]), re.IGNORECASE
)
re_year_mention = re.compile(r"\d\d\d\d")
re_month_year_mention = re.compile(r"\d\d[-/.]\d\d")

TIME_WORDS = [
    "now",
    # periods in the day
    "afternoon",
    "morning",
    "evening",
    "noon",
    # interval markers
    "after",
    "before",
]
re_time_mention = re.compile(
    "|".join([rf"\b{word}\b" for word in TIME_WORDS]), re.IGNORECASE
)
re_time_am_pm = re.compile(r"\d *[ap]m", re.IGNORECASE)
re_time = re.compile(r"\d:\d", re.IGNORECASE)


def has_date_mentioned(text: str):
    """Helper to determine if a text mentions something that looks like a date."""
    return (
        len(re_date_mention.findall(text)) > 0
        or len(re_year_mention.findall(text)) > 0
        or len(re_month_year_mention.findall(text)) > 0
    )


def has_time_mentioned(text: str):
    """Helper to determine if a text mentions something that looks like a time."""
    return (
        len(re_time_mention.findall(text)) > 0
        or len(re_time_am_pm.findall(text)) > 0
        or len(re_time.findall(text)) > 0
    )


def parse_duckling_datetime(res: dict):
    """Parses the provided text using the duckling data from the context."""
    if res["dim"] != "time":
        return res

    # We only look at the first value for now
    value = res["value"]

    # Check whether we have date / time mentions to help us decide on
    # the type of value we are dealing with
    has_date = has_date_mentioned(res["body"])

    if value["type"] == "value":
        time_string = value["value"]
        grain = value["grain"]
        datetime_val_tz = date_parser.parse(time_string)
        datetime_val = datetime_val_tz.replace(tzinfo=None)

        # We have to decide what type of value we're dealing with
        if grain in ["second", "minute", "hour"]:
            # If we have an time component, we need to check if there's a date component too
            if has_date:
                return get_datetime_dict("datetime", datetime_val.isoformat())
            else:
                return get_datetime_dict("time", datetime_val.isoformat()[11:])
        elif grain == "day":
            # we're dealing with a day
            return get_datetime_dict("date", datetime_val.strftime("%Y-%m-%d"))
        elif grain in ["week", "month", "year"]:
            # we're dealing with a multi-day interval
            if grain == "week":
                delta = relativedelta(days=7)
            elif grain == "month":
                delta = relativedelta(months=1)
            else:
                delta = relativedelta(years=1)

            datetime_end_val = datetime_val + delta
            start_date = datetime_val.strftime("%Y-%m-%d")
            end_date = datetime_end_val.strftime("%Y-%m-%d")

            return get_datetime_dict("date_interval", start_date, end_date)
        else:
            logger.error(f"Found unknown duckling grain in: {json.dumps(value)}")

    elif value["type"] == "interval":
        # we work only with the grain of the "from" component (or the "to" if it's the only one)
        grain = (
            value["from"]["grain"] if value.get("from") else value["to"]["grain"]
        )

        datetime_from = (
            date_parser.parse(value["from"]["value"]).replace(tzinfo=None)
            if value.get("from")
            else None
        )
        datetime_to = (
            date_parser.parse(value["to"]["value"]).replace(tzinfo=None)
            if value.get("to")
            else None
        )

        # Tweak to the evening interval, make it 6pm to 11pm (rather than midnight)
        if datetime_to and datetime_from:
            if (
                datetime_to - datetime_from
            ).total_seconds() == 60 * 60 * 6 and datetime_from.hour == 18:
                datetime_to = datetime_from + relativedelta(hours=5)

        if grain in ["second", "minute", "hour"]:
            if not has_date:
                start_time = (
                    datetime_from.isoformat()[11:] if datetime_from else None
                )
                end_time = datetime_to.isoformat()[11:] if datetime_to else None

                return get_datetime_dict("time_interval", start_time, end_time)
            else:
                start_datetime = (
                    datetime_from.isoformat() if datetime_from else None
                )
                end_datetime = datetime_to.isoformat() if datetime_to else None

                return get_datetime_dict(
                    "datetime_interval", start_datetime, end_datetime
                )
        else:
            # Otherwise it's a date interval
            start_date = datetime_from.isoformat()[11:] if datetime_from else None
            end_date = datetime_to.isoformat()[11:] if datetime_to else None

            return get_datetime_dict("date_interval", start_date, end_date)
    else:
        raise Exception(f"Unknown duckling value type: {value['type']}")

    return None


def date_to_str(dt, value_format: str):
    dt_val = parser.parse(dt["value"])
    if value_format == "friendly":
        weekday = dt_val.strftime("%A")
        month = dt_val.strftime("%B")

        day = str(dt_val.day)
        if day[-1] == "1" and (len(day) == 1 or day[-2] != "1"):
            day += "st"
        elif day[-1] == "2" and (len(day) == 1 or day[-2] != "1"):
            day += "nd"
        elif day[-1] == "3" and (len(day) == 1 or day[-2] != "1"):
            day += "rd"
        else:
            day += "th"

        # e.g. "Friday, 5th October"
        return f"{weekday}, {month} {day}"

    elif value_format == "relative":
        pass

    return dt["value"]


def time_to_str(dt, value_format: str):
    try:
        dt_val = datetime.strptime(dt["value"], "%H:%M:%S.%f")
    except ValueError:
        dt_val = datetime.strptime(dt["value"], "%H:%M:%S")

    if value_format == "friendly":
        hour = dt_val.hour
        am_pm = "am"
        if hour >= 12:
            am_pm = "pm"
            if hour > 12:
                hour -= 12

        # We want 12am not 0am
        if hour == 0:
            hour = 12

        if dt_val.minute > 0:
            return f"{hour}:{dt_val.minute:02d}{am_pm}"
        else:
            res = f"{hour}{am_pm}"
            if res == "12pm":
                return "noon"
            elif res == "12am":
                return "midnight"
            else:
                return res

    elif value_format == "relative":
        pass

    return dt_val.strftime("%H:%M:%S")


def datetime_to_str(dt, value_format: str):
    date_part = date_to_str({"type": "date", "value": dt["value"][0:10]}, value_format)

    time_part = time_to_str({"type": "time", "value": dt["value"][11:]}, value_format)

    return date_part + " at " + time_part


def date_interval_to_str(dt, value_format: str):
    if dt["from_value"] and dt["to_value"]:
        return (
            "from "
            + date_to_str(dt["from_value"], value_format)
            + " until "
            + date_to_str(dt["to_value"], value_format)
        )
    elif dt["from_value"]:
        return "from " + date_to_str(dt["from_value"], value_format)
    else:
        return "until " + date_to_str(dt["to_value"], value_format)


def time_interval_to_str(dt, value_format: str):
    if dt["from_value"] and dt["to_value"]:
        res = (
            "from "
            + time_to_str(dt["from_value"], value_format)
            + " until "
            + time_to_str(dt["to_value"], value_format)
        )

        if value_format == "friendly":
            if res == "from 4am until noon":
                return "in the morning"
            elif res == "from noon until 7pm":
                return "in the afternoon"
            elif res == "from 6pm until 11pm":
                return "evening"

        return res

    elif dt["from_value"]:
        return "from " + time_to_str(dt["from_value"], value_format)
    else:
        return "until " + time_to_str(dt["to_value"], value_format)


def datetime_interval_to_str(dt, value_format: str):
    if dt.get("from_value") and dt.get("to_value"):
        # If it's the same day, we use the time interval
        if dt["from_value"]["value"][0:10] == dt["to_value"]["value"][0:10]:
            from_time = dt["from_value"]["value"][11:]
            to_time = dt["to_value"]["value"][11:]

            return (
                date_to_str(dt["from_value"], value_format)
                + ", "
                + time_interval_to_str(
                    {
                        "type": "time_interval",
                        "value": f"{from_time} to {to_time}",
                        "from_value": {"type": "time", "value": from_time},
                        "to_value": {"type": "time", "value": to_time},
                    },
                    value_format,
                )
            )
        else:
            return (
                "from "
                + datetime_to_str(dt["from_value"], value_format)
                + " until "
                + datetime_to_str(dt["to_value"], value_format)
            )

    elif dt.get("from_value"):
        return "from " + datetime_to_str(dt["from_value"], value_format)
    else:
        return "until " + datetime_to_str(dt["to_value"], value_format)


def _format_datetime(dt: dict, value_format: str):
    if value_format in ["default", "relative", "friendly"]:
        if dt["type"] == "date":
            return date_to_str(dt, value_format)
        elif dt["type"] == "time":
            return time_to_str(dt, value_format)
        elif dt["type"] == "datetime":
            return datetime_to_str(dt, value_format)
        if dt["type"] == "date_interval":
            return date_interval_to_str(dt, value_format)
        elif dt["type"] == "time_interval":
            return time_interval_to_str(dt, value_format)
        elif dt["type"] == "datetime_interval":
            return datetime_interval_to_str(dt, value_format)
    elif value_format in ["date"]:
        # We need to extract the date from a datetime
        return get_datetime_dict("date", dt["value"][0:10])
    elif value_format in ["time"]:
        # We need to extract the time from a datetime
        return get_datetime_dict("time", dt["value"][11:])

    # For any cases not caught
    return dt["value"]


def nlg_formatter(value: any, value_formats: Optional[List[str]] = None):
    """A more advanced formatter that can deal with objects, DateTime and multi-language.

    :param value: The value to be formatted.
    :param value_formats: A list of strings describing the formats to use for the output.
    """
    if value_formats is None or len(value_formats) == 0:
        value_formats = ["default"]

    for value_format in value_formats:
        # We try to detect automatically certain types
        if isinstance(value, str):
            if re_iso_date.match(value):
                value = get_datetime_dict("date", value)
            elif re_iso_time.match(value):
                value = get_datetime_dict("time", value)
            elif re_iso_datetime.match(value):
                value = get_datetime_dict("datetime", value)

        if isinstance(value, dict):
            if value.get("_type") == "DateTime":
                value = _format_datetime(value, value_format)
            elif isinstance(value, dict) and "name" in value:
                value = value["name"]

    return value
