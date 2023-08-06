# encoding: utf-8
# module datify

"""An extensible library that provides the functionality of the parsing strings in different formats to extract dates.

**Datify** makes it easy to extract dates from strings in *(nearly)* any formats.

You will need only to parse the date string with Datify, and it's all good.

The date formats supported by Datify are the following:

* Day first digit-only dates: 20.02.2020, 09/07/2000, 9-1-2005;
* Month first digit-only dates: 02 22 2020, 09.07.2000, 1.9/2005;
* Dates in the general date format: 2020-04-15;
* **Alphanumeric dates in different languages**: 11th of July 2020; 6 липня 2021; 31 декабря, 2021.

Month locales supported: English, Russian, Ukrainian.
It is possible to add more month name localizations. See the documentation of DatifyConfig class for more information.

===
Extended version of the library tour can be found at GitHub: https://github.com/mitryp/datify/
"""

from __future__ import annotations

import enum
import re
import warnings
from datetime import datetime
from typing import Optional, Union, Sequence

from datify.deprecation_warning import deprecated


def _is_same_word(str1: str, str2: str) -> bool:
    """Tries to figure if given strings are the same words in different forms.

    :param str1: str
    :param str2: str
    :return: bool
    """

    return (len(set(str1).difference(set(str2))) < len(str1) / 2) and (
            len(set(str2).difference(set(str1))) < len(str2) / 2) and (
               str1[0:2] == str2[0:2] if len(str1) < 4 else str1[0:3] == str2[0:3])


def _get_words_list(string: str) -> Optional[list]:
    """Returns a list of words in a string split with supported separators.
    If the string does not contain any separators, returns the list with one element of the string.

    :param string: the string to be split into words
    :return: the list of words in the string
    """

    return re.split(DatifyConfig.separators_pattern(), string)


def _get_alphabetic_month_ordinal(month_name: str) -> int | None:
    """Returns an integer representing the ordinal of the given month name.

    If the given string cannot be interpreted as a valid month name, returns None.

    :param month_name: a month name to be parsed to an integer ordinal
    :return: the ordinal of the given month name if the valid month name is given, else None
    """

    normalized_month_name = _normalize_month_name(month_name)

    # check if the month name itself is contained in any of the month name sets
    for n in range(len(DatifyConfig.months)):
        if normalized_month_name in DatifyConfig.months[n]:
            return n + 1

    # check if the month name appears to be another form of the month name contained in the sets
    for n in range(len(DatifyConfig.months)):
        for month in DatifyConfig.months[n]:
            if _is_same_word(normalized_month_name, month):
                return n + 1

    return None


def _parse_string(string, year_defined: bool = False, month_defined: bool = False, day_defined: bool = False) -> tuple[
        int | None, int | None, int | None]:
    """Temporary function to parse a string into a tuple of (year, month, day).

    :param string: a string to parse
    :return: tuple of integers: (year, month, day)
    """

    # if all the date parts are defined by the user, don't parse the string
    if year_defined and month_defined and day_defined:
        return None, None, None

    # try to find the general date format
    general_date_match = string_match(DatifyConfig.date_format(), string)
    if general_date_match is not None:
        # clear the match from separators
        clean_date = re.sub(DatifyConfig.separators_pattern(), '', general_date_match)

        # parse the date parts, cast them to integers
        year = int(clean_date[:4])
        month = int(clean_date[4:6])
        day = int(clean_date[6:8])

        return tuple((year, month, day))

    # split into date parts with separators
    words = _get_words_list(string)

    year, month, day = (None,) * 3

    # to prevent losing the alphabetic month names when the day_first is set to False, try to find the alphabetic month
    # before the actual parsing
    if not DatifyConfig.day_first:
        for word in words:
            potential_month_ordinal = _get_alphabetic_month_ordinal(word)
            if potential_month_ordinal is not None:
                words.remove(word)
                month_defined = True
                month = potential_month_ordinal
                break

    parts_remaining = _DatePart.order(year_defined, month_defined, day_defined)

    for word in words:
        for date_part in parts_remaining:
            part_match = string_match(date_part.value, word)

            # if the part is not matching the current pattern, then it may be a month
            if part_match is None:
                # if the month was already defined, skip the part
                if month is not None:
                    continue

                # try to define the month ordinal
                month_ordinal = _get_alphabetic_month_ordinal(word)

                # if unsuccessful, skip the part
                if month_ordinal is None:
                    continue

                # define the month ordinal and remove month from the parts_remaining
                month = month_ordinal
                parts_remaining.remove(_DatePart.month)
                continue

            # parse the value of the part into an integer
            value = int(part_match)

            # set the value to the corresponding date part variable
            if date_part == _DatePart.day:
                day = value
            elif date_part == _DatePart.month:
                month = value
            else:
                year = value

            # remove the part from the parts_remaining
            parts_remaining.remove(date_part)

    return year, month, day


class DatifyConfig:
    splitters: set[str] = {' ', '/', '.', '-'}
    """The set of the splitters to be found in the parsed strings."""

    day_first: bool = True
    """The option to determine whether the day or the month should be found first"""

    day_format: str = r'\b(([1-9])|([12]\d)|(3[01]))(\b|(?=\D))'
    """The pattern matching the day of the date."""

    month_format_digit: str = r'\b((0?[1-9])|(1[012]))\b'
    """The pattern matching the digit representation of the month of the date."""

    year_format: str = r'\b[12]\d\d\d\b'
    """The pattern matching the year of the date."""

    _date_format: str = r'\b[12]\d\d\d$$((0[1-9])|(1[012]))$$(([012]\d)|(3[01]))\b'
    """The pattern matching the general date format with the '$$' placeholders at the places where the separator 
    patterns should be placed."""

    months: list[set[str]] = [
        {'january', 'jan', 'січень', 'январь'},
        {'february', 'feb', 'лютий', 'февраль'},
        {'march', 'mar', 'березень', 'март'},
        {'april', 'apr', 'квітень', 'апрель'},
        {'may', 'травень', 'май'},
        {'june', 'jun', 'червень', 'июнь'},
        {'july', 'jul', 'липень', 'июль'},
        {'august', 'aug', 'серпень', 'август'},
        {'september', 'sep', 'вересень', 'сентябрь'},
        {'october', 'oct', 'жовтень', 'октябрь'},
        {'november', 'nov', 'листопад', 'ноябрь'},
        {'december', 'dec', 'грудень', 'декабрь'}
    ]
    """The list of sets representing the specified month names. New localizations can be added with the DatifyConfig 
    methods 
    'add_month_name(int, str)' and 'add_months_locale(Sequence[str])'.
    """

    @classmethod
    def separators_pattern(cls) -> str:
        """Returns a pattern that matches any supported separators."""

        # replace is needed because the re.escape() escapes the `space` character for some reason
        return f"({'|'.join(map(re.escape, cls.splitters))})".replace('\\ ', ' ')

    @classmethod
    def date_format(cls) -> str:
        """Returns a date format with the separator placeholder replaced with the latest separator pattern."""

        return cls._date_format.replace('$$', f'{cls.separators_pattern()}?')

    @classmethod
    def add_month_name(cls, ordinal: int, name: str) -> None:
        """Adds a new name to the month names set with the given ordinal.

        The `ordinal` argument is the number of the month the name to be added to. It must be in range of [1, 12]
        inclusive, otherwise the ValueError will be raised.

        :param ordinal: the ordinal of the month the new name to be added to
        :param name: a new name to be added to the month
        :return: None
        """

        # check if the ordinal is within the specified range
        if ordinal not in range(1, 13):
            raise ValueError('Invalid month ordinal {}. Month ordinals must be in range from 1 to 12 inclusive'
                             .format(ordinal))

        # add a normalized month name to the month names set with the given ordinal
        cls.months[ordinal].add(_normalize_month_name(name))

    @classmethod
    def add_months_locale(cls, locale: Sequence[str]):
        """The method to add a localization of months to the Datify config.

        The `locale` argument is a sequence of unique strings with the length of 12 representing the months names
        ordered in the month order.

        If the sequence has the length that is not equal to 12 or contains not unique elements, the Value

        :param locale:
        :return:
        """

        # check the length of the sequence
        set_length = len(set(locale))
        if len(locale) != 12 or set_length != 12:
            raise ValueError('Invalid number of months: {}. `locales` must be a collection of 12 unique month names '
                             'ordered in the months order'.format(set_length))

        # add each month to the config
        for i in range(len(cls.months)):
            cls.months[i].add(_normalize_month_name(locale[i]))


class _DatePart(enum.Enum):
    """The enum representing a date part during the date parsing process.

    Each date part has a corresponding format RegExp pattern that matches the part.

    _DatePart.order() returns a tuple consisting of the date parts based on the DatifyConfig.day_first setting and the
    date parts that are already defined.
    """

    year = DatifyConfig.year_format
    month = DatifyConfig.month_format_digit
    day = DatifyConfig.day_format

    @staticmethod
    def order(year_defined: bool = False, month_defined: bool = False, day_defined: bool = False) -> list[_DatePart]:
        """Returns a list of the date parts ordered according to the DatifyConfig.day_first setting.

        The returned list does not include the date parts that were already defined before.

        :param year_defined: whether to include the year part in the returned list
        :param month_defined: whether to include the month part in the returned list
        :param day_defined: whether to include the day part in the returned list
        :return: list of the parts ordered in the parsing order not including the parts that were already defined
        """
        res: list[_DatePart]

        # specify the initial order based on the day_first setting of the datify config
        if DatifyConfig.day_first:
            res = [_DatePart.day, _DatePart.month, _DatePart.year]
        else:
            res = [_DatePart.month, _DatePart.day, _DatePart.year]

        # remove the date parts that were already defined before
        if year_defined:
            res.remove(_DatePart.year)

        if month_defined:
            res.remove(_DatePart.month)

        if day_defined:
            res.remove(_DatePart.day)

        return res


class Datify:
    config: DatifyConfig = DatifyConfig

    # deprecated functionality left for backwards compatibility, will be removed at 2.0.0
    splitters: set
    day_format_digit: str
    day_format_alnum: str
    month_format_digit: str
    year_format: str
    date_format: str
    day_first: bool

    year: int | None
    month: int | None
    day: int | None

    def __init__(self, user_input: str | None = None, year: int | None = None,
                 month: int | None = None, day: int | None = None):
        """Creates a new Datify instance.

        If the user_input argument is given, it will be parsed to extract a date parts from the input.
        Also, can take separate parameters `year`, `month` and `day`.
        If those are given, they will override the corresponding parsed values.

        **The signature will be changed to Datify(year: int?, month: int?, day: int?) in the version 2.0.0.**
        **To parse the string the Datify.parse(string) factory will be used then. Consider changing to that method right
        now.**

        :param user_input: str: a string input to be parsed into a date parts
        :param year: int: the value of the year to force set to the year field
        :param month: int: the value of the month to force set to the month field
        :param day: int: the value of the day to force set to the day field
        """
        self.setup_variables()  # deprecated functionality left for backwards compatibility, will be removed in 2.0.0
        self._initialize_datify()

        if user_input is not None:
            warnings.warn('`user_input` argument is deprecated since 1.1.0 and will be removed in 2.0.0, please '
                          'consider using Datify.parse(string) instead', DeprecationWarning, stacklevel=2)
            self.year, self.month, self.day = _parse_string(user_input)

        if year is not None:
            self.year = year

        if month is not None:
            self.month = month

        if day is not None:
            self.day = day

    @classmethod
    def parse(cls, string: str, year: int | None = None, month: int | None = None, day: int | None = None) -> Datify:
        """Parses the given string and returns a Datify object with the parsed values.

        Tries to extract a year, month and day from the string according to the DatifyConfig settings.

        Can also take an optional year, month and day as arguments. The given values of the parameters are force set
        to the corresponding fields of the Datify object returned.

        Can parse the following formats:

        * Digit-only (or separated with a supported separators) general date format: YYYY$?MM$?DD - e.g. '2021.12.31',
          '2022-01-20', '20220214' etc.;
        * Common separated digit date format: DD$MM$YYYY - e.g. '31.12.2021', '20.1.2022', '14.02.2022' etc.;
        * American separated digit date format (month is first): MM$DD$YYYY - e.g. '12.31.2021', '01.20.2022',
          '2.14.2022' etc.;
        * **Date formats with localized month names** - e.g. '31st of December 2021', '1 квітня 2022', '14 февраля 2022'
          etc.

        In the formats above, the `$` sign stands for any of the supported date separators, which are stored in the
        `DatifyConfig.splitters` field. The external splitters can be added - see the DatifyConfig documentation.
        The `$?` sign stands for optional supported separator (can or can not be present in the input string).

        The following month locales are supported:

        * English (January)
        * English shortened (Jan)
        * Ukrainian (січень)
        * Russian (январь)

        You can also add new locales to the DatifyConfig with the methods below:

        * DatifyConfig.add_month_name(cls, ordinal: int, name: str) - adds a new name for the month with the given
          ordinal number. If the ordinal is not in the range of [1, 12] inclusive, the ValueError will be raised.
          For instance, to add a new name for the 3rd month, the following syntax is used:

          ```DatifyConfig.add_month_name(3, 'march')```
        * DatifyConfig.add_months_locale(cls, locale: Sequence[str]) - adds a new locale for the month names.
          The `locale` argument is a sequence of unique strings with the length of 12. The month names should be ordered
          in the month order. If the length of the sequence is not equal to 12 or the sequence contains duplicates, the
          ValueError is raised.

        :param string: an input string to be parsed into a Datify object
        :param year: a predefined year to be force set
        :param month: a predefined month to be force set
        :param day: a predefined day to be force set
        :return: Datify object with the values parsed from the input string
        """

        parsed_year, parsed_month, parsed_day = _parse_string(string)
        d = Datify(None, year or parsed_year, month or parsed_month, day or parsed_day)
        return d

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_date_part(string: str) -> bool:
        """Returns True if the given string contains parts of date in formats supported by Datify.
        Otherwise, returns False.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param string: Takes str
        :return: bool
        """

        words = _get_words_list(string)
        if words:
            for word in words:
                if any((
                        Datify.is_day(word),
                        Datify.is_digit_month(word),
                        Datify.is_alpha_month(word),
                        Datify.is_year(word)
                )):
                    return True

            return False

        else:
            return any((
                Datify.is_day(string),
                Datify.is_digit_month(string),
                Datify.is_alpha_month(string),
                Datify.is_year(string),
                Datify.is_date(string)
            ))

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_date(date: str | int) -> bool:
        """Returns True if given parameter suits format of date ('YYYYMMDD' by default).
        Otherwise, returns False.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param date: Takes str
        :return: bool
        """

        date = str(date)
        return re.match(DatifyConfig.date_format(), date) is not None

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def find_date(string: str) -> str | None:
        """Returns date in general date format from given string if present.
        Otherwise, returns None.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param string: Takes str
        :return: str | None
        """

        res = re.search(DatifyConfig.date_format(), string)
        return res.group(0) if res else None

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_day(day: str | int) -> bool:
        """Returns True if the given argument suits the day format: e.g. '09' or '9,' or '9th'.
        Otherwise, returns False.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param day: Takes str
        :return: bool
        """

        day = str(day)
        return re.match(DatifyConfig.day_format, day) is not None

    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def set_day(self, day: int | str) -> None:
        """Sets day of the Datify object.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param day: Takes str or int
        :return: no return
        """

        day = str(day).strip()

        if Datify.is_day(day):
            if day.isdigit():
                self.day = int(day)
                return

            day_re = re.search(DatifyConfig.day_format, day)
            if day_re:
                day_str = day_re.group(0)
                self.day = int(day_str)

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_digit_month(month: str | int) -> bool:
        """Returns True if the given parameter suits digit month format: e.g. '09' or '9'.
        Otherwise, returns False.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param month: Takes str or int
        :return: Bool
        """

        month = str(month).strip()
        return re.match(DatifyConfig.month_format_digit, month) is not None

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_alpha_month(string: str) -> bool:
        """Returns True if given parameter suits alpha month format: e.g. 'January' or 'jan' or 'серпень' or 'серпня'.
        Otherwise, returns False.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param string: Takes str
        :return: Bool
        """

        return Datify.get_alpha_month(string) is not None

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def get_alpha_month(string: str) -> int | None:
        """Returns number of given month name. If not found, returns None.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param string: Takes str
        :return: int or None
        """

        return _get_alphabetic_month_ordinal(_normalize_month_name(string))

    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def set_month(self, month: str | int) -> None:
        """Sets month of the Datify object. Takes number of a month or its name.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param month: Takes str or int
        :return: no return
        """

        month = str(month).strip()

        if Datify.is_digit_month(month):
            self.month = int(month)
            return

        if Datify.is_alpha_month(month):
            self.month = Datify.get_alpha_month(month)

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def is_year(year: Union[str, int]) -> bool:
        """Returns True if given parameter is suitable for the year format: e.g. '14' or '2014'.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param year: Takes str
        :return: Bool
        """

        year = str(year).strip()
        return re.match(DatifyConfig.year_format, year) is not None

    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def set_year(self, year: Union[str, int]) -> None:
        """Sets the year of the Datify object.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :param year: Takes str or int
        :return: no return
        """

        year = str(year).strip()
        if Datify.is_year(year):
            self.year = int(year)

    @property
    def complete(self):
        """The property that returns True if the date of the datify object is complete.
        Otherwise, returns False.

        The datify object is considered complete if all the fields are not None.

        :return: True if the date of the datify object is complete, False otherwise
        """

        return self.year is not None and self.month is not None and self.day is not None

    def date(self) -> datetime | None:
        """Returns a datetime object if the date of the Datify instance is complete.
        Otherwise, returns None.

        Will be changed to a property in the 2.0.0.

        :return: datetime object if the date is complete, None otherwise
        """

        if not self.complete:
            return None

        return datetime(year=self.year, month=self.month, day=self.day)

    def tuple(self) -> tuple[int | None, int | None, int | None]:
        """Returns the tuple of all parameters in the following order:
        **(day, month, year)**.

        Will be changed to a property returning **(year, month, day)** in 2.0.0.

        :return: tuple[int | None, int | None, int | None]
        """

        return self.day, self.month, self.year

    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0')
    def date_or_tuple(self) -> Union[datetime, tuple]:
        """
        Returns datetime object if all needed parameters are known. Otherwise, returns tuple of all parameters.
        It's not recommended using as return different types, but in some cases it may be useful.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :return: datetime object or tuple
        """

        try:
            return datetime(year=self.year, month=self.month, day=self.day)

        except TypeError:
            return self.tuple()

    @staticmethod
    @deprecated('The methods with rare usage cases are not supported anymore', since='1.1.0', removed='2.0.0',
                silent=True)
    def setup_variables() -> None:
        """Sets the class variables according to Datify.config values.

        Deprecated since 1.1.0. Will be removed in 2.0.0.

        :return: None
        """

        Datify.splitters = DatifyConfig.splitters
        Datify.day_format_digit = DatifyConfig.day_format
        Datify.day_format_alnum = DatifyConfig.day_format
        Datify.month_format_digit = DatifyConfig.month_format_digit
        Datify.year_format = DatifyConfig.year_format
        Datify.date_format = DatifyConfig.date_format()
        Datify.day_first = DatifyConfig.day_first

    def _initialize_datify(self) -> None:
        """Initializes the Datify instance with the initial values of None."""
        self.day, self.month, self.year = (None,) * 3

    def __repr__(self) -> str:
        """Returns a string representation of the Datify object.

        :return: str
        """

        return f'<Datify[year={self.year}, month={self.month}, day={self.day}]>'


def _normalize_month_name(name: str) -> str:
    """Returns a stripped and lowercase string from the given string.

    :param name: a string to be normalized
    :return: the normalized string
    """

    return name.strip().lower()


def string_match(pattern: str, string: str) -> str | None:
    """Returns the first string match of the given pattern in the given string.

    :param pattern: the pattern to match against the string
    :param string: the string to match with the pattern
    :return: string matching the given pattern or None if no match was found
    """

    match = re.search(pattern, string)
    return match.group(0) if match is not None else None
