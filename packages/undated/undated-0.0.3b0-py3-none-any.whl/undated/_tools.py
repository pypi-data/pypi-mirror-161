"""
YMD class and associated functions. Imported by init.

**ASSUMPTIONS**
    See init, no further assumptions to note

**LIMITATIONS**
    See init, no further limitations to note
"""
# -----------------------------------------------

from __future__ import annotations
from typing import Any, Optional, Tuple, Union

from . import _core as udc

# -----------------------------------------------

_EPOCH = 1

INVALID = 0
VALID = 1
TRUSTED = 2

# -----------------------------------------------


def _get_parts(year_or_iymd: int, month: int, day: int) -> Tuple[int, int, int, int]:
    """ Creates the date parts tuple from the provided data. """

    if month is None:  # Assume year_or_ymd is Ymd or Ym format
        if year_or_iymd < 9999_99:
            year_or_iymd = (year_or_iymd * 100) + 1

        return (
            year_or_iymd,
            year_or_iymd // 1_00_00,
            (year_or_iymd % 1_00_00) // 1_00,
            year_or_iymd % 1_00
        )

    # Assume seperate parts provided

    return (
        (year_or_iymd * 1_00_00) + (month * 1_00) + (day or 1),
        year_or_iymd, month, (day or 1)
    )


# -----------------------------------------------


class YMD:
    """
    Class of date parts, year, month, day

    :param year_or_iymd: the year, date in Ymd format or tuple of date parts
    :param month: the month number, 1 = Jan, defaults to 1
    :param day: the day. If not supplied, the 1st is assumed
    :param trusted: True, if dates can be trusted to be correct, the validation stage is skipped
    """

    iymd: Optional[int]
    """ The date as an 8 digit integer, in year, month, day format """

    year: Optional[int]
    """ The year element of the date, as a 4 digit integer """

    month: Optional[int]
    """ The month element of the date, as a 1 or 2 digit integer. January==1, December==12 """

    day: Optional[int]
    """ The day element of the date, as a 1 or 2 digit integer """

    status: int = None
    """ The status of the class. Refers to the package constants VALID, INVALID and TRUSTED """

    # ---

    def __init__(
            self,
            year_or_iymd: Union[int, tuple, None],
            month: int = None,
            day: int = None,
            trusted: bool = False
    ):
        """ Initialises the YMD class """

        # ---

        def invalidate():
            """ Sets the properties to the invalid state """
            self.iymd = self.year = self.month = self.day = None
            self.status = INVALID

        # ---

        self._properties = {}

        if year_or_iymd is None:
            invalidate()
            return

        if isinstance(year_or_iymd, tuple):
            if len(year_or_iymd) == 3:
                self.year, self.month, self.day = year_or_iymd
                self.iymd = udc.glue_parts(self.year, self.month, self.day)
            else:
                invalidate()
                return
        else:
            self.iymd, self.year, self.month, self.day = _get_parts(year_or_iymd, month, day)

        if trusted:
            self.status = TRUSTED
        elif udc.is_valid(self.year, self.month, self.day):
            self.status = VALID
        else:
            invalidate()

    # ---
    # Comparison magic methods

    def __lt__(self, other: int) -> bool:
        """ Called on comparison using < operator """
        return self.iymd < other

    def __le__(self, other: int) -> bool:
        """ Called on comparison using <= operator """
        return self.iymd <= other

    def __eq__(self, other: int) -> bool:
        """ Called on comparison using == operator """
        return self.iymd == other

    def __ne__(self, other: int) -> bool:
        """ Called on comparison using != operator """
        return self.iymd != other

    def __ge__(self, other: int) -> bool:
        """ Called on comparison using >= operator """
        return self.iymd >= other

    def __gt__(self, other: int) -> bool:
        """ To get called on comparison using > operator """
        return self.iymd > other

    # ---
    # Operator magic methods

    def __add__(self, other: int) -> YMD:
        """ Called on add operation using + operator. In calendar days """
        return add_days(self, other)

    def __sub__(self, other: Union[int, YMD]) -> Union[int, YMD]:
        """ Called on subtraction operation using - operator. In calendar days """
        if isinstance(other, int):
            return add_days(self, other * -1)
        return days_between(self, other)

    # ---
    # Type conversion magic methods

    def __bool__(self):
        """ Called by built-int bool() method to convert a type to a bool """
        return bool(self.status != INVALID)

    def __int__(self):
        """ Called by built-int int() method to convert a type to an int """
        return self.iymd

    def __repr__(self):
        """ Called by built-int repr() method to return a readable representation of the type """
        return self.iymd

    def __str__(self):
        """ Called by built-int str() method to convert a type to a str """
        return str(self.iymd)

    # ---
    # Restrict attribute updates

    def __setattr__(self, key: str, value: Any):
        """ Assurance that the date has not been manually modifed """

        if self.status:
            raise Exception('Unable to modified YMD')
        self.__dict__[key] = value

    # ---
    # Private modules

    def _get_property(self, name: int) -> Any:
        """
        Gets the ymd date property. Added when first needed,
         rather than at initialisation, for performance.
         Only _EPOCH at the moment, but more may be added.

        :param name: str, the property name; [_EPOCH]
        :return: the property value
        """

        if self.status == INVALID:
            return None

        if name not in self._properties:
            if name == _EPOCH:
                self._properties[name] = udc.epoch_from_parts(self.year, self.month, self.day)

        return self._properties[name]

    # ---
    # Public modules

    def add_days(self, days: int) -> YMD:
        """
        Adds the specified number of days to the date.
        Another option would be to use the addition operator ```ymd2 = ymd1 + 2```

        :param days: The number of days to add. Use negative days to subtract days.
        :return: YMD class object
        """

        return add_days(self, days)

    # ---

    def add_months(self, months: int, period: bool = False) -> YMD:
        """
        Adds the specified number of months to the date

        :param months: The number of months to add, use negative months to subtract
        :param period: Set to True when looking for a period end date.
          So... With period False, Jan 1st + 12 months, would be 1st Jan the following year.
          With period set to True, it would be 31st Dec the same year.
        :return: YMD class object
        """

        return add_months(self, months, period)

    # ---

    def add_weekdays(self, weekdays: int) -> YMD:
        """
        Adds the specified number of weekdays, Monday to Friday, to the date

        :param weekdays: The number of weekdays to add. Use negative days to subtract.
        :return: YMD class object
        """

        return add_weekdays(self, weekdays)

    # ---

    def add_years(self, years: int, period: bool = False) -> YMD:
        """
        Adds a specified number of years to the date

        :param years: The number of years to add. Use negative years to subtract
        :param period: Set to True when looking for a period end date.
          So... With period False, Jan 1st + 1 year, would be 1st Jan the following year.
          With period set to True, it would be 31st Dec the same year.
        :return: YMD class object
        """

        return add_months(self, years * 12, period=period)

    # ---

    def day_of_week(self) -> Union[int, None]:
        """
        The number for the day of the week. Sunday == 0, Monday == 1...

        :return: The day number 0 to 6
        """

        if self.status == INVALID:
            return None
        return udc.day_of_week(self._get_property(_EPOCH))

    # ---

    def epoch(self) -> Union[int, None]:
        """
        An epoch value for the date, # TODO try to exclude from sphinx

        :return: int, the epoch value
        """

        return self._get_property(_EPOCH)

    # ---

    def is_leap_year(self) -> bool:
        """
        Is the date falling within a leap year

        :return: True when the date falls in a leap year
        """

        if self.status == INVALID:
            return False
        return bool(udc.is_leap_year(self.year))

    # ---

    def is_weekday(self) -> bool:
        """
        Is the date falling on a weekday, IE between Monday and Friday

        :return: True when it is a weekday
        """

        if self.status == INVALID:
            return False
        return 0 < udc.day_of_week(self._get_property(_EPOCH)) < 6


# ---

INVALID_YMD = YMD(0)

# -----------------------------------------------


def add_days(ymd: YMD, days: int) -> YMD:
    """
    Adds a number of days to a date in in Ymd format

    :param ymd: YMD class object
    :param days: int, the number of days to add
    :return: YMD class object
    """

    if ymd.status == INVALID:
        return INVALID_YMD
    return epoch_to_ymd(ymd.epoch() + days)


# -----------------------------------------------


def add_months(ymd: YMD, months: int, period: bool = False) -> YMD:
    """
    Adds given months to a date. Use negative months to subtract months

    :param ymd: YMD class object
    :param months: int, the number of months
    :param period: bool, takes the previous day. EG: For last day of a period
    :return: YMD class object
    """

    if ymd.status == INVALID:
        return INVALID_YMD

    year, month, day = udc.add_months(ymd.year, ymd.month, ymd.day, months)
    if period:
        return epoch_to_ymd(udc.epoch_from_parts(year, month, day) + (1 if months < 0 else -1))
    return YMD(year, month, day, trusted=True)


# -----------------------------------------------


def add_weekdays(ymd: YMD, weekdays: int) -> YMD:
    """
    Adds a number of weekdays, monday to friday, to a date in in Ymd format

    :param ymd: YMD class object
    :param weekdays: int, the number of days to add
    :return: YMD class object
    """

    if ymd.status == INVALID:
        return INVALID_YMD

    return YMD(
        *udc.add_weekdays(ymd.epoch(), weekdays),
        trusted=True
    )


# -----------------------------------------------


def days_between(from_ymd: YMD, to_ymd: YMD) -> Union[int, None]:
    """
    Calculates the days between two dates

    :param from_ymd: YMD, the from date YMD class object
    :param to_ymd: YMD, the to date YMD class object
    :return: int, the days between the dates
    """

    if INVALID in [from_ymd.status, to_ymd.status]:
        return None
    return to_ymd.epoch() - from_ymd.epoch()


# -----------------------------------------------


def epoch_to_ymd(epoch: int) -> YMD:
    """
    Converts the epoch day number to a YMD class object

    :param epoch: int, the epoch value
    :return: YMD class object
    """

    return YMD(*udc.epoch_to_parts(epoch), trusted=True)


# -----------------------------------------------


def months_between(from_ymd: YMD, to_ymd: YMD) -> Union[int, None]:
    """
    Calculates the complete months between two dates

    :param from_ymd: YMD class object
    :param to_ymd: YMD class object
    :return: int, the complete months between the dates
    """

    if INVALID in [from_ymd, to_ymd.status]:
        return None

    if from_ymd.iymd < to_ymd.iymd:
        ymd1 = from_ymd
        ymd2 = to_ymd
        pos_neg = 1
    else:
        ymd1 = to_ymd
        ymd2 = from_ymd
        pos_neg = -1

    # ---

    if ymd2.day == udc.DAYS_IN_MONTH[udc.is_leap_year(ymd2.year)][ymd2.month]:
        day_factor = 0
    else:
        day_factor = 1 if ymd2.day < ymd1.day else 0

    # ---

    return (((ymd2.year - ymd1.year) * 12) + ymd2.month - ymd1.month - day_factor) * pos_neg


# -----------------------------------------------


def quarter(ymd: YMD, to_str: bool = True) -> Union[int, str, None]:
    """
    Calculates the quarter from a year, returning the quarter end month, or quarter number

    :param ymd: YMD class object
    :param to_str: bool, true returns 2021Q3, otherwise 202103 format
    :return: str 2021Q1, 2021Q2, 2021Q3, 2021Q4; or int 202103, 202106, 202109, 202112
    """

    if ymd.status == INVALID:
        return None
    return udc.quarter(ymd.year, ymd.month, to_str)


# -----------------------------------------------


def weekdays_between(from_ymd: YMD, to_ymd: YMD, inclusive: bool = False) -> Union[int, None]:
    """
    Calculates the number of weekdays between two dates

    :param from_ymd: YMD class object
    :param to_ymd: YMD class object
    :param inclusive: bool, whether to include the to date as a completed day
    :return: int, the number of days between the dates
    """

    if INVALID in [from_ymd.status, to_ymd.status]:
        return None

    return udc.weekdays_between_epochs(
        from_ymd.epoch(),
        to_ymd.epoch(),
        inclusive
    )


# -----------------------------------------------
# End.
