"""
Core functions for the undated modules

**ASSUMPTIONS**
    See init, no further assumptions to note

**LIMITATIONS**
    See init, no further limitations to note
"""
# -----------------------------------------------

import datetime

from typing import Tuple, Union

# -----------------------------------------------

DAYS_IN_MONTH = (
    (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),  # Non leap year
    (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)   # Leap year
)

DAYS_SO_FAR = (
    (0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365),  # Non leap year
    (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366)   # Leap year
)

THIS_YEAR = int(datetime.date.today().strftime('%Y'))

# -----------------------------------------------


def add_months(year: int, month: int, day: int, months: int) -> Tuple[int, int, int]:
    """
    Adds given months to a date. Use negative months to subtract months
    :param year: int, the year
    :param month: int, the month
    :param day: int, the day
    :param months: int, the number of months to add
    :return: tuple, the date parts
    """

    month += months

    if month > 12:
        year += (month - 1) // 12
        month = ((month - 1) % 12) + 1
    elif month < 1:
        year -= (abs(month) + 12) // 12
        month = 12 - (abs(month) % 12)

    day = min(day, DAYS_IN_MONTH[0 if month != 2 else is_leap_year(year)][month])

    return year, month, day


# -----------------------------------------------


def add_weekdays(epoch: int, weekdays: int) -> Tuple[int, int, int]:
    """
    Adds a number of weekdays, monday to friday, to an epoch
    :param epoch: int, the date in epoch form
    :param weekdays: int, the number of days to add
    :return: tuple, the date parts
    """

    weeks, days = weekdays // 5, weekdays % 5
    weekday = day_of_week(epoch)
    weekend_adjust = 0 if 0 < weekday + days < 6 else 2
    days_to_add = (weeks * 7) + days + weekend_adjust
    return epoch_to_parts(epoch + days_to_add)


# -----------------------------------------------


def day_of_week(epoch: int) -> int:
    """
    Calculates the day of the week from the epoch value
    :param epoch: int, the epoch value, see epoch functions
    :return: int, the epoch value
    """

    return (epoch - 1) % 7


# -----------------------------------------------


def epoch_to_parts(epoch: int) -> Tuple[int, int, int]:
    """
    Converts the epoch day number to a YMD class
    :param epoch: int, the epoch value
    :return: tuple, the date parts
    """

    year, day = epoch // 365, epoch % 365

    if day == 0:
        year -= 1
        day = 365

    prior_year = year - 1
    day -= (prior_year // 4) - (prior_year // 100) + (prior_year // 400)

    while day <= 0:  # Allowing for leap years may cause negative days, shouldn't loop many times
        year -= 1
        day += 366 if is_leap_year(year) else 365

    leap_year = is_leap_year(year)

    month = 1
    while DAYS_SO_FAR[leap_year][month + 1] < day:
        month += 1

    day -= DAYS_SO_FAR[leap_year][month]

    return year, month, day


# -----------------------------------------------


def epoch_from_parts(year: int, month: int, day: int) -> int:
    """
    Gets the epoch, number of days for calculations, returns the epoch value
    :param year: int, the year
    :param month: int, the month
    :param day: int, the day
    :return: int, the epoch value
    """

    prior_year = year - 1

    return (
            (year * 365)
            + (prior_year // 4) - (prior_year // 100) + (prior_year // 400)
            + DAYS_SO_FAR[is_leap_year(year)][month] + day
    )


# -----------------------------------------------


def explode_iymd(iymd: int) -> Tuple[int, int, int]:
    """
    Explodes the int iymd date into it year, month, day parts
    :param iymd: int, the date in Ymd or Ym format
    :return: tuple, the date parts
    """

    if iymd < 9999_99:
        iymd = (iymd * 100) + 1

    return iymd // 1_00_00, (iymd % 1_00_00) // 1_00, iymd % 1_00


# -----------------------------------------------


def glue_parts(year: int, month: int, day: int) -> int:
    """
    Glues the date parts into a Ymd format int
    :param year: int, the year
    :param month: int, the month
    :param day: int, the day
    :return: int, the date in Ymd format
    """

    return (year * 1_00_00) + (month * 1_00) + (day or 1)


# -----------------------------------------------


def is_leap_year(year: int) -> int:
    """
    Is the year a leap year
    :param year: int, the year
    :return: int, 1 for leap year, 0 not a leap year
    """

    return 1 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 0


# -----------------------------------------------


def is_valid(year: int, month: int, day: int) -> bool:
    """
    Validates the sepecifed date parameters are valid
    :param year: int, the year
    :param month: int, the month, Jan = 1
    :param day: int, the day of the month
    :return: bool, whether valid or not
    """

    try:
        if not 1582 < year < 10000:
            return False
        if not 0 < month < 13:
            return False
        if not 0 < day <= DAYS_IN_MONTH[1][month]:
            return False
        if day == 29 and month == 2 and not is_leap_year(year):
            return False
        return True
    except ValueError:
        return False


# -----------------------------------------------


def is_weekday(year: int, month: int, day: int) -> bool:
    """
    Calculates if the date is a weekday, Monday - Friday
    :param year: int, the year
    :param month: int, the month, Jan = 1
    :param day: int, the day of the month
    :return: bool, true when it is a weekday
    """

    return 0 < day_of_week(epoch_from_parts(year, month, day)) < 6


# -----------------------------------------------


def quarter(year: int, month: int, to_str: bool = True) -> Union[int, str]:
    """
    Calculates the quarter from a year, returning the quarter end month, or quarter number
    :param year: int, the year
    :param month: int, the month
    :param to_str: bool, true returns 2021Q3, otherwise 202103 format
    :return: str 2021Q1, 2021Q2, 2021Q3, 2021Q4; or int 202103, 202106, 202109, 202112
    """

    month -= 1
    if to_str:
        return f'{year}Q{month // 3 + 1}'
    return (year * 100) + ((month // 3) + 1) * 3


# -----------------------------------------------


def weekdays_between_epochs(from_epoch: int, to_epoch: int, inclusive: bool = False) -> int:
    """
    Calculates the number of weekdays (mon-fri) between two epochs
    :param from_epoch: int, the from date epoch
    :param to_epoch: int, the to date epoch
    :param inclusive: bool, whether to include the to date as a completed day
    :return: int, the number of week
    """

    epoch1 = min(from_epoch, to_epoch)
    epoch2 = max(from_epoch, to_epoch)

    ymd1w = day_of_week(epoch1)
    ymd2w = day_of_week(epoch2)

    return (
        (((epoch2 - epoch1) // 7 * 5)
         + (min(ymd2w, 5) - min(ymd1w, 5))
         + (5 if ymd2w < ymd1w else 0)    # extra_days
         + (1 if inclusive else 0))       # last_day
        * (-1 if to_epoch < from_epoch else 1)  # positive or negative
    )


# -----------------------------------------------
# End.
