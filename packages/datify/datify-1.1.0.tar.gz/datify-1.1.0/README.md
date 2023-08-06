**Version 1.1.0 introduced logic reconsidering based on the [Dart implementation](https://github.com/mitryp/datifyDart). 
That version changed the library configuration approach, allowing to extend the localizations and more.
The configuration after that version is not compatible with the 1.0.X and 0.X.X versions of Datify.
Moreover, most of the methods in the library are deprecated since 1.1.0 and will be removed in 2.0.0, so it will break 
the existing code that uses that methods.**

**Since 1.1.0, the library will warn the users that continue using the deprecated methods.**

## Automatic flexible date extracting from strings in any formats.

**Datify** makes it easy to extract dates from strings in _(nearly)_ any formats.

You will need only to parse the date string with Datify, and it's all good.

The date formats supported by Datify are the following:

* Day first digit-only dates: 20.02.2020, 09/07/2000, 9-1-2005;
* Month first digit-only dates: 02 22 2020, 09.07.2000, 1.9/2005;
* Dates in the general date format: 2020-04-15;
* **Alphanumeric dates in different languages**: 11th of July 2020; 6 липня 2021; 31 декабря, 2021.

See the [Formats](#formats) section for the detailed information about the supported formats.

The behavior of Datify can be configured with the DatifyConfig - see [Configuration](#configuring-datify) section.

### Month name languages supported by default:

- [x] English
- [x] Ukrainian
- [x] Russian

---

## Installing
Simply run `pip install datify` from your command line (pip must be installed).

## Data parsing

To extract a date from a string, use the `.parse(string)` factory of the `Datify` class.
The method takes an input string and the optional parameters `year`, `month`, and `day`.

After that the input string will be parsed. If the optional parameters were given, the respective object fields will
have the provided values.

### Getting the result

After the parsing is done, the result can be retrieved in a different ways:

* If the date is complete, the result can be transformed into a `datetime` object with the `date()` getter.
  > **!** The `date()` getter will be replaced with the `date` property in **2.0.0**.

  However, if the date is incomplete the getter will return None.

  The result is considered complete when the `year`, `month`, and `day` fields of the result are not None.

  To make sure the parsed result is complete and can be transformed to a datetime, the `complete` property is used.
  It returns True if the result is complete and can be transformed int a datetime object.


* To get the not nullable result independent of the parsing result, use the `tuple()` getter.

  It will return a tuple of the following structure: `(day, month, year)` where each element represents the 
  corresponding field of the Datify object.
  > **!** The `tuple()` getter will be replaced with the `tuple` property that returns the tuple of the structure 
    (year, month, day) in **2.0.0**.

* The Datify instance itself has the `year`, `month`, and `day` mutable nullable fields, that can be used to access
  the parsing result.

## Formats

> In the formats below, the sign `$` represents any of the supported date splitters.
>
> The `$?` sign represents an optional separator character (the separator may or may not be present).

- General date format: `YYYY$?MM$?DD` - e.g. _20210706_ or _2022-02-23_ etc;

- `Alphanumeric dates in different languages` - e.g. _6th of July 2021_, _31st of December 2021_, _20 жовтня_, _1 июля_
  etc;
  > Datify tries to find different forms of month names in the natural languages where they are present.

When the `day_first` is set to `true`:

- The most common digit-only date format: `DD$MM$YYYY` - e.g. _20.01.2022_;

When the `day_first` is set to `false`:

- American digit date format (the month is first): `MM$DD$YYYY` - e.g. _12.31.2021_;

> When the `day_first` is set to `false`, Datify will try to find the alphabetic month names before the parsing to avoid
losing the month values in the strings of the format '1 of July 2020'. However, this makes the parsing a bit slower with
this option enabled.

## Configuring Datify

The library behavior can be customized with the `DatifyConfig` class fields and methods.

The following can be customized:

1. Date splitters (`.`, `/`, `-`, ` ` by default).

   Any of the supported splitters can be present in digit-only or alphanumeric dates (See [Formats](#formats) section
   of the documentation).

   To define a new custom separator, it must be added to the `DatifyConfig.splitters` set.

   For instance, to add the `#` separator to the config, the following syntax is used:
   ```python
   DatifyConfig.splitters.add('#')
   ```
   After that the next `Datify.parse()` invocations will use the added splitter in the parsing operations.
   > A splitter can also be string more than one character long


2. Month names localizations, different month aliases.
   By default, Datify supports English, English shortened, Ukrainian and Russian month names:
   `{'january','jan','січень','январь',}`

   More localizations can be added whenever they needed with the `DatifyConfig`:


  * To add a new month name for the specified month, the `DatifyConfig.add_month_name(ordinal: int, name: str)` method
    is used. The `ordinal` argument takes int number in range [1, 12] inclusive to represent the month number.

    For example, to add the French name, `Septembre`, for the 9th month, the following syntax is used:
    ```python
    DatifyConfig.add_month_name(9, 'Septembre')
    ```
    _If the `ordinal` is not in the defined range, the ValueError will be raised._


* To add a new entire localization, which consists of the 12 ordered month names, the
  `DatifyConfig.add_months_locale(locale: Iterable[str])` method is used.

  > The `locale` iterable must have a length of 12 and consist of the unique elements
  If these conditions are not satisfied, the ArgumentError will be thrown.

  For example, to add the French month localization, the following syntax is used:
  ```python
  french_months = (
     'Janvier', 'Février', 'Mars', 'Avril', 'Peut', 'Juin',
     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 
     'Décembre'
   )
  
  DatifyConfig.add_months_locale(french_months)
  ```
  > Note: The months should be ordered in the months order for the correct work.

> `DatifyConfig` can be accessed with Datify.config field
---

## Example:

Unnecessary code was omitted from the example above. See the `example/datify_example.py` for the full code example.
```python
class Events(abc.ABC):
    """Database emulation for the example.

    This class stores dates and the corresponding event descriptions and provides the method for
    record requesting from the storage.
    """
    _records = {
        Date(year=2021, month=12, day=31): 'New Year party 🎄',
        Date(year=2022, month=1, day=20): 'Birthday celebration 🎁',
        Date(year=2022, month=2, day=14): 'St. Valentines Day 💖',
        Date(year=2022, month=2, day=23): 'The cinema attendance 📽',
        Date(year=2022, month=5, day=23): 'A long-awaited Moment 🔥',
    }
    """Stores the dates and the corresponding event descriptions."""

    @classmethod
    def query(cls, year: int | None = None, month: int | None = None, day: int | None = None) -> str | None:
        """Returns an event descriptions based on the provided date parts.

        If no date parts provided or no corresponding event descriptions are found, the method returns None.
        """

        # handle empty requests
        if all((year is None, month is None, day is None)):
            return None

        # return the first string corresponding to the Date that satisfies the query, if any
        for record_date in cls._records:
            if record_date.satisfies(year, month, day):
                return cls._records[record_date]

        return None


def handle_request(search_request: SearchRequest) -> str:
    """Handles the SearchRequest requests.

    Returns a corresponding event description or the error message.
    """
    date_query = search_request['date']

    # Datify handles all the parsing inside freeing from even thinking about it!
    parsed = Datify.parse(date_query)

    response = Events.query(year=parsed.year, month=parsed.month, day=parsed.day)

    return response if response is not None else 'No events found for this query 👀'


if __name__ == '__main__':
    # define dates in the different formats
    dates = (
        '31.12.2021',  # common digit-only date format
        '2022-02-23',  # another commonly-used date format
        '23-02/2022',  # the supported separators can be combined in the string
        '20 of January',  # date is incomplete but still correctly parsed
        'May',  # just a month name
        '14 лютого 2022',  # Ukrainian date which stands for 14.02.2022
        'not a date',  # not a date at all
    )

    # 'request' all the dates and print the result
    for date in dates:
        print(f'{date}: {handle_request({"date": date})}')
```
