"""
The utils module functionality mirrors that of the ``ud.YMD`` class.
However these functions have been stripped down to improve performance.
Use only when dates are valid integers in the ``Ymd`` format.
"""
# -----------------------------------------------

from typing import Union

from . import _core as udc
from . import _tools as udt

# -----------------------------------------------


def add_days(iymd: int, days: int) -> int:
    """
    Adds a number of days to a date in in Ymd format

    :param iymd: the date in Ymd format
    :param days: the number of days to add
    :return: the new date in Ymd format
    """

    return udc.glue_parts(
        *udc.epoch_to_parts(udc.epoch_from_parts(*udc.explode_iymd(iymd)) + days)
    )


# -----------------------------------------------


def add_months(iymd: int, months: int) -> int:
    """
    Adds given months to a date. Use negative months to subtract months

    :param iymd: the date in Ymd format
    :param months: the number of months
    :return: the new date
    """

    return udc.glue_parts(*udc.add_months(*udc.explode_iymd(iymd), months))


# -----------------------------------------------


def add_weekdays(iymd: int, weekdays: int) -> int:
    """
    Adds a number of weekdays, monday to friday, to a date in in Ymd format

    :param iymd: the date in Ymd format
    :param weekdays: the number of days to add
    :return: the new date in Ymd format
    """

    return udc.glue_parts(
        *udc.add_weekdays(udc.epoch_from_parts(*udc.explode_iymd(iymd)), weekdays)
    )


# -----------------------------------------------


def day_of_week(iymd: int) -> int:
    """
    Calculates the number for day of the week. Sunday = 0, Monday = 1...

    :param iymd: date in Ymd format
    :return: the day number 0 to 6
    """

    return (udc.epoch_from_parts(*udc.explode_iymd(iymd)) - 1) % 7


# -----------------------------------------------


def days_between(from_iymd: int, to_iymd: int) -> int:
    """
    Calculates the days between two dates

    :param from_iymd: the from date in Ymd format
    :param to_iymd: the to date in Ymd format
    :return: the days between the dates
    """

    return (
        udc.epoch_from_parts(*udc.explode_iymd(to_iymd))
        - udc.epoch_from_parts(*udc.explode_iymd(from_iymd))
    )


# -----------------------------------------------


def is_leap_year(year: int) -> int:
    """
    Is the year a leap year

    :param year: the year
    :return: 1 for leap year, 0 not a leap year
    """

    return udc.is_leap_year(year)


# -----------------------------------------------


def is_valid(iymd: int) -> bool:
    """
    Checks the date is valid. Year expected to be between 1583 and 9999

    :param iymd: the date in Ymd format
    :return: is the date is a valid date or not
    """

    return udc.is_valid(*udc.explode_iymd(iymd))


# -----------------------------------------------


def is_weekday(iymd: int) -> bool:
    """
    Calculates if the date is a weekday, Monday - Friday

    :param iymd: the date in Ymd format
    :return: True when it is a weekday
    """

    return udc.is_weekday(*udc.explode_iymd(iymd))


# -----------------------------------------------


def months_between(from_iymd: Union[int, udt.YMD], to_iymd: Union[int, udt.YMD]) -> int:
    """
    Calculates the complete months between two dates

    :param from_iymd: the from date in Ymd or Ym format
    :param to_iymd: the from date in Ymd or Ym format
    :return: the complete months between the dates
    """

    from_ymd = udt.YMD(from_iymd) if isinstance(from_iymd, int) else from_iymd
    to_ymd = udt.YMD(to_iymd) if isinstance(to_iymd, int) else to_iymd
    return udt.months_between(from_ymd, to_ymd)


# -----------------------------------------------


def quarter(iymd: int, to_str: bool = True) -> Union[int, str]:
    """
    Calculates the quarter from a year, returning the quarter end month, or quarter number

    :param iymd: the date in Ymd or Ym format
    :param to_str: true returns 2021Q3, otherwise 202103 format
    :return: str 2021Q1, 2021Q2, 2021Q3, 2021Q4; or int 202103, 202106, 202109, 202112
    """

    parts = udc.explode_iymd(iymd)
    return udc.quarter(parts[0], parts[1], to_str)


# -----------------------------------------------


def weekdays_between(from_iymd: int, to_iymd: int, inclusive: bool = False) -> int:
    """
    Calculates the complete months between two dates

    :param from_iymd: the from date in Ymd format
    :param to_iymd: the from date in Ymd format
    :param inclusive: whether to include the to date as a completed day
    :return: the complete months between the dates
    """

    return udc.weekdays_between_epochs(
        udc.epoch_from_parts(*udc.explode_iymd(from_iymd)),
        udc.epoch_from_parts(*udc.explode_iymd(to_iymd)),
        inclusive
    )


# -----------------------------------------------
# End.
