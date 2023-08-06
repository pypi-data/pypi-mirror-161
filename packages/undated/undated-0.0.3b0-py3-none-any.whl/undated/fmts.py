"""
The ``fmts`` (formattings) module comes into play when the date data format is unknown.
It has two key class objects. The ``Deriver`` class derives the date format from a list
of dates, returning an ``UndatedFormat`` class object, which contains the information
required by the ``as_parts`` function to extract the date elements.
"""
# -----------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from typing import Union

from . import _core as udc
from . import _data as udd

# -----------------------------------------------

PIVOT_YEAR = udc.THIS_YEAR - 80

# -----------------------------------------------
# Keys

YEAR = 'year'
MONTH = 'month'
DAY = 'day'

# ---
# Hints

Y2 = 101
YFIRST = 102
YLAST = 103
YM = 104

# ---
# Params

HINTS = 201
LANGUAGES = 202
TIME_SEPARATOR = 203
YY_PIVOT = 204

# ---
# Steps

SEPARATORS = 301
TEXT_MONTH = 302
TIME_LOOP = 303
TIME_ONCE = 304
Y2_TO_Y4 = 305

# -----------------------------------------------


def _int_only_up_to_char(sdate, char):
    """  Returns ints up to to the specified character """

    sdate_char = ''.join(filter((lambda c: c.isdigit() or c == char), sdate))
    if sdate_char.count(char) == 1:
        sdate_split0 = sdate.split(char)[0]
        if len(sdate_split0) > 7:
            sdate_split0_digits = ''.join(filter((lambda c: c.isdigit()), sdate_split0))
            if len(sdate_split0_digits) < 9:
                return sdate_split0
    return None


# -----------------------------------------------


def _remove_time(sdate: str) -> str:
    """ Uses common format rules to remove the time element from the string """

    sdate_digits = ''.join(filter((lambda c: c.isdigit()), sdate))

    if len(sdate_digits) > 8:

        if sdate.count('T') == 1 and sdate.count(' ') == 0:
            sdate = _int_only_up_to_char(sdate, 'T')

        elif sdate.count(' ') == 1:
            sdate = _int_only_up_to_char(sdate, ' ')

        elif ' ' in sdate:
            sdate = sdate.rsplit(' ', 1)[0]
            _remove_time(sdate)

    return sdate


# -----------------------------------------------


def _split_int(value: int, split: Union[list, tuple], keys: Union[list, tuple]):
    """ Splits the int value into potential date parts  """

    results = []
    for i in reversed(split):
        factor = 10 ** i
        results.insert(0, value % factor)
        value = value // factor

    return dict(zip(keys, results))


# -----------------------------------------------


def _split_str(string: str) -> list:
    """ Splits a string based on the change from numbers to strings """

    last_char = string[:1].isdigit()
    new_string = ''
    for i in string:
        digit = i.isdigit()
        if last_char != digit:
            new_string += '\t'
        new_string += i
        last_char = digit
    return new_string.split('\t')


# -----------------------------------------------


def _separators(sdate):
    """ Standardises the separator to a tab character """

    for sep in [' ', '-', '/', '.']:
        sdate = sdate.replace(sep, '\t')

    return sdate.strip('\t')


# -----------------------------------------------


def _standardise_text(sdate: str) -> str:
    """ Standardises the date string to get a better match """

    return sdate.upper().replace('Ä', 'A').replace('É', 'E').replace('Û', 'U')


# -----------------------------------------------


def _text_month(sdate: str, steps: dict) -> str:
    """ Processes the date if text is found within the date string """

    sdate = _standardise_text(sdate)
    step = steps[TEXT_MONTH]

    # ---

    if isinstance(step, tuple):  # (language, position, used_parts)
        parts = sdate.split('\t') if '\t' in sdate else _split_str(sdate)
        for i, month in enumerate(udd.MONTH_NAMES[step[0]]):
            if month == parts[step[1]]:
                parts[step[1]] = str(i + 1).zfill(2)
                break
        return '\t'.join([parts[i] for i in step[2]])

    # ---

    separators = SEPARATORS in steps

    if isinstance(step, list):
        langs = step
    elif isinstance(step, str):
        langs = [step]
    else:
        langs = list(udd.MONTH_NAMES)

    for lang in langs:
        for i, month in enumerate(udd.MONTH_NAMES[lang]):
            if separators:
                month = f'\t{month}\t'
            if month in sdate:
                return sdate.replace(month, str(i + 1).zfill(2))

    return sdate  # Month not found


# -----------------------------------------------


def _validated_yy_pivot(yy_pivot: int) -> int:
    """ Validates the yy_pivot parameter, returns the default if not specified """

    if yy_pivot is None:
        return PIVOT_YEAR
    if 1582 < yy_pivot < 9999:
        return yy_pivot
    raise ValueError(f'Invalid yy_pivot value: {yy_pivot}')


# -----------------------------------------------


def _y2_to_y4(year: int, yy_pivot: int) -> int:
    """ Converts two digit year to four digits """

    return year + ((yy_pivot // 100) + (1 if year < (yy_pivot % 100) else 0)) * 100


# -----------------------------------------------


class Deriver:
    """ Facilitates the searching of dates to derive the format """

    def __init__(self):
        """ Set the class variables """

        self.params = {
            HINTS: [],
            LANGUAGES: [],
            TIME_SEPARATOR: 'T',
            YY_PIVOT: PIVOT_YEAR
        }

    # ---
    # Private methods

    def _evolve_idate(self, idate: Union[list, int], split: tuple) -> dict:
        """ Common evolution steps """

        idate_split = (
            _split_int(idate, *split) if isinstance(idate, int)
            else dict(zip(split[1], [int(i) for i in idate]))
        )

        if idate_split[YEAR] < 100:
            idate_split[YEAR] = _y2_to_y4(idate_split[YEAR], self.params[YY_PIVOT])
        if DAY not in idate_split:
            idate_split[DAY] = 1

        return idate_split

    # ---

    def _get_splits(self, dlen) -> list:
        """ Gets the splits depending on the hints """

        splits = udd.SPLITS['6Y2' if dlen == 6 and Y2 in self.params[HINTS] else dlen]
        if YFIRST in self.params[HINTS]:
            splits = [split for split in splits if split[1][0] == YEAR]
        elif YLAST in self.params[HINTS]:
            splits = [split for split in splits if split[1][-1] == YEAR]
        return splits

    # ---

    def _expunge_time(self, sdate: str, steps: dict) -> str:
        """ Uses common format rules to remove the time element from the string """

        if self.params[TIME_SEPARATOR] is None:
            return sdate

        sdate_digits = ''.join(filter((lambda c: c.isdigit()), sdate))

        if len(sdate_digits) > 8:

            if sdate.count(self.params[TIME_SEPARATOR]) == 1 and sdate.count(' ') == 0:
                sdate = _int_only_up_to_char(sdate, self.params[TIME_SEPARATOR])
                steps[TIME_ONCE] = self.params[TIME_SEPARATOR]

            elif sdate.count(' ') == 1:
                sdate = _int_only_up_to_char(sdate, ' ')
                steps[TIME_ONCE] = ' '

            elif ' ' in sdate:
                while ' ' in sdate and len(sdate_digits) > 8:
                    sdate = sdate.rsplit(' ', 1)[0]
                    sdate_digits = ''.join(filter((lambda c: c.isdigit()), sdate))
                steps[TIME_LOOP] = None

        return sdate

    # ---

    def _only_digits(self, sdate: str, dlen: int) -> list[tuple]:
        """ Process the date if only digits exist """

        idate = int(sdate)
        results = []
        # ---
        splits = self._get_splits(dlen)

        for split in splits:
            idate_split = self._evolve_idate(idate, split)
            if udc.is_valid(**idate_split):
                results.append(split)

        return results

    # ---

    def _separated_digits(self, sdate: str, dlen: int) -> list[tuple]:
        """ Process the date if only seperated digits exist """

        results = []
        parts = sdate.split('\t')
        len_parts = len(parts)
        splits = self._get_splits(dlen)

        for split in splits:
            if len(split[1]) == len_parts:
                idate_split = self._evolve_idate(parts, split)
                if udc.is_valid(**idate_split):
                    results.append(split)

        return results

    # ---

    def _text_month(self, sdate: str, steps: dict) -> list[tuple]:
        """ Processes the date if text is found within the date string """

        # Disabling too many locals, as they are required here to be more descriptive
        # pylint: disable=too-many-locals

        formats = []
        sdate = _standardise_text(sdate)
        orig_parts = sdate.split('\t') if '\t' in sdate else _split_str(sdate)
        used_parts = []

        # ---

        found = self._text_month_find(orig_parts, used_parts)
        if not found:
            return []

        lang, orig_part_no, month_no, used_part_no = found

        # ---

        idate_parts = [month_no if i == orig_part_no else orig_parts[i] for i in used_parts]
        dlen = len(''.join(idate_parts))
        len_parts = len(idate_parts)
        if dlen == 6 and len_parts == 3 and Y2 not in self.params[HINTS]:
            self.params[HINTS].append(Y2)
        splits = self._get_splits(dlen)

        for split in splits:
            if len(split[1]) == len_parts and split[1][used_part_no] == MONTH:
                idate_split = self._evolve_idate(idate_parts, split)
                if udc.is_valid(**idate_split):
                    formats.append(split)

        # ---

        if orig_part_no is not None:
            steps[TEXT_MONTH] = (lang, orig_part_no, used_parts)

            if len(formats) > 1 and dlen == 6 and len_parts == 3:
                # As text is present, assume year is last.
                formats = [r for r in formats if r[1][2] == YEAR]
                if len(formats) == 1:
                    steps[Y2_TO_Y4] = self.params[YY_PIVOT]

        # ---

        return formats

    # ---

    def _text_month_find(self, orig_parts, used_parts) -> Union[tuple, None]:
        """ Extention of _text_month. Searches for possible languages """

        possible_languages = {}

        lang_months = [
            (lng, mth) for lng, mth in udd.MONTH_NAMES.items()
            if not self.params[LANGUAGES] or lng in self.params[LANGUAGES]
        ]

        for i, part in enumerate(orig_parts):
            if part.isdigit():
                used_parts.append(i)
            else:
                for lang, months in lang_months:
                    for imon in [_i for _i, _m in enumerate(months) if part == _m]:
                        possible_languages[lang] = (i, str(imon + 1).zfill(2), len(used_parts))
                        used_parts.append(i)
                        break

        # ---

        if len(possible_languages) > 1:
            self.params[LANGUAGES] = list(possible_languages)
            return None

        if not possible_languages:
            return None

        # ---

        lang = list(possible_languages)[0]
        return (lang, *possible_languages[lang])

    # ---
    # Public methods

    def search(self, dates: Union[list, str, tuple]) -> Union[UndatedFormat, None]:
        """
        Search through a list of dates to derive the date format

        .. caution::

           All of the dates in the list passed to the search method
           are expected to be in the same format.

        :param dates: list or tuple of dates to search. Or str for one date
        :return: the derived ``UndatedFormat`` object
        """

        if isinstance(dates, str):
            dates = [dates]

        # ---

        adjust_len = (2 if Y2 in self.params[HINTS] else 0) + (2 if YM in self.params[HINTS] else 0)
        expected_len = 8 - adjust_len

        # ---

        for sdate in dates:
            sdate = str(sdate)
            steps = {}
            if Y2 in self.params[HINTS]:
                steps[Y2_TO_Y4] = self.params[YY_PIVOT]
            if not sdate.isdigit():
                sdate = self._expunge_time(sdate, steps)
            if sdate.isdigit():
                formats = (
                    self._only_digits(sdate, expected_len)
                    if expected_len - 2 < len(sdate) <= expected_len
                    else []
                )
            else:
                sdate = _separators(sdate)
                no_seps = sdate.replace('\t', '')
                if sdate != no_seps:
                    steps[SEPARATORS] = None
                if no_seps.isdigit() and expected_len - 2 < len(no_seps) <= expected_len:
                    formats = self._separated_digits(sdate, expected_len)
                else:
                    formats = self._text_month(sdate, steps)

            # ---

            if formats and len(formats) == 1:
                return UndatedFormat(formats[0][0], formats[0][1], steps, True)

        # ---

        return None

    # ---

    def set_parameters(self, params: dict):
        """
        Sets the optional parameters for the search

        :param params: see tutorial for possible parameters
        """

        for key, val in params.items():
            if key in [HINTS, LANGUAGES] and isinstance(val, str):
                val = [val]
            elif key == YY_PIVOT:
                val = _validated_yy_pivot(val)
            # ---
            if key == LANGUAGES:  # Expand two character codes
                langs = []
                for lang in val:
                    if len(lang) == 2:
                        langs.extend([f'{lang}1', f'{lang}2'])
                    else:
                        langs.append(lang)
                self.params[key] = langs
            else:
                self.params[key] = val


# -----------------------------------------------


@dataclass
class UndatedFormat:
    """
    Properties for the format.
    Created by the ``Deriver`` class or ``convert_format`` function
    """

    split: list[int, int, int]
    keys: list[str, str, str]
    steps: dict
    valid: bool


# -----------------------------------------------


def as_parts(
        sdate: Union[int, str],
        fmt: Union[str, UndatedFormat],
        yy_pivot: int = None) -> Union[tuple, None]:
    """
    Converts the sdate to year, month, day, based on the format

    :param sdate: The date as a str or int
    :param fmt: The date format, as either a basic format as a string, or a derived format
    :param yy_pivot: The pivot year for two digit years. Use with string based formats
    """

    if not sdate or not fmt:
        return None

    # ---

    udfmt = convert_format(fmt, yy_pivot) if isinstance(fmt, str) else fmt
    if not udfmt.valid:
        return None

    # ---

    if TIME_ONCE in udfmt.steps:
        sdate = _int_only_up_to_char(sdate, udfmt.steps[TIME_ONCE])

    if TIME_LOOP in udfmt.steps:
        sdate_digits = ''.join(filter((lambda c: c.isdigit()), sdate))
        while ' ' in sdate and len(sdate_digits) > 8:
            sdate = sdate.rsplit(' ', 1)[0]
            sdate_digits = ''.join(filter((lambda c: c.isdigit()), sdate))

    if SEPARATORS in udfmt.steps:
        sdate = _separators(sdate)

    if TEXT_MONTH in udfmt.steps and isinstance(sdate, str):
        sdate = _text_month(sdate, udfmt.steps)

    # ---

    if isinstance(sdate, str):
        if sdate.isdigit():
            sdate = int(sdate)
        else:
            sdate = int(''.join(filter((lambda c: c.isdigit()), sdate)))

    parts = _split_int(sdate, udfmt.split, udfmt.keys)

    # ---

    if parts[YEAR] < 100:
        parts[YEAR] = _y2_to_y4(parts[YEAR], _validated_yy_pivot(udfmt.steps.get(Y2_TO_Y4)))

    # ---

    if udc.is_valid(**parts):
        return parts['year'], parts['month'], parts['day']
    return None


# -----------------------------------------------


def convert_format(fmt: str, yy_pivot: int = None) -> UndatedFormat:
    """
    Converts the basic string format into an ``UndatedFormat`` object.
    Recommended when looping, to prevent repeated format conversion.

    :param fmt: The string format. See the tutorial for valid values.
    :param yy_pivot: The pivot year for two digit years. Use only with string based formats.
    """

    split = []
    keys = []
    steps = {}

    if 'M' in fmt:
        steps[TEXT_MONTH] = None

    if '-' in fmt:
        steps[SEPARATORS] = None

    for i in fmt:
        if i == 'y':
            split.append(2)
            keys.append(YEAR)
            steps[Y2_TO_Y4] = _validated_yy_pivot(yy_pivot)
        elif i == 'Y':
            split.append(4)
            keys.append(YEAR)
        elif i in ['m', 'M']:
            split.append(2)
            keys.append(MONTH)
        elif i == 'd':
            split.append(2)
            keys.append(DAY)

    return UndatedFormat(split, keys, steps, len(split) == 3)


# -----------------------------------------------
# End.
