from functools import reduce
from io import StringIO
import requests
import csv
import numpy

from .storage import _load_from_storage
from .request import request_url, web_url

DELIMITER = '\t'
ENCODING = 'ISO-8859-1'
GLOSSARY_FOLDER = 'glossary/lookups'
_memory = {}
MISSING_VALUE = '-'
MISSING = -99999


def _is_missing_value(value): return value == MISSING_VALUE or value == MISSING or value == str(MISSING)


def _replace_missing_values(value: str): return str(MISSING) if str(value) == '-' else value


def _rewrite_csv_file_as_tab(filepath: str):
    with open(filepath, 'r', encoding=ENCODING) as fp:
        reader = csv.reader(fp)
        for row in reader:
            yield DELIMITER.join(list(map(_replace_missing_values, row)))


def _rewrite_csv_text_as_tab(text: str):
    reader = csv.reader(StringIO(text))
    for row in reader:
        yield DELIMITER.join(list(map(_replace_missing_values, row)))


def _recfromcsv(data): return numpy.recfromcsv(data,
                                               missing_values=MISSING_VALUE,
                                               filling_values=MISSING,
                                               delimiter=DELIMITER,
                                               encoding=ENCODING)


def _memory_wrapper(key: str, func):
    global _memory
    _memory[key] = _memory[key] if key in _memory else func()
    return _memory[key]


def load_lookup(filepath: str, keep_in_memory: bool = False):
    """
    Import local lookup table as csv file into a `numpy.recarray`.

    Parameters
    ----------
    filepath : str
        The path of csv file on the local file system.
    keep_in_memory: bool
        Set to True if you want to store the file in memory for later use.

    Returns
    -------
    numpy.recarray
        The `numpy.recarray` converted from the csv content.
    """
    def load(): return _recfromcsv(_rewrite_csv_file_as_tab(filepath))
    return _memory_wrapper(filepath, load) if keep_in_memory else load()


def _download_lookup_data(filename: str):
    filepath = f"{GLOSSARY_FOLDER}/{filename}"

    def fallback():
        url = request_url(f"{web_url()}/{filepath}")
        return requests.get(url).content.decode('utf-8')

    try:
        data = _load_from_storage(filepath, glossary=True)
        return data.decode('utf-8') if data else None
    except ImportError:
        return fallback()


def download_lookup(filename: str, keep_in_memory: bool = True):
    """
    Download lookup table from Hestia as csv into a `numpy.recarray`.

    Parameters
    ----------
    filename : str
        The name on the file on the Hestia lookup repository.
    keep_in_memory: bool
        Set to False if you do NOT want to store the file in memory for later use.

    Returns
    -------
    numpy.recarray
        The `numpy.recarray` converted from the csv content.
    """
    def load(): return _recfromcsv(_rewrite_csv_text_as_tab(_download_lookup_data(filename)))

    try:
        return _memory_wrapper(filename, load) if keep_in_memory else load()
    except Exception:
        return None


def column_name(key: str):
    """
    Convert the column name to a usable key on a `numpy.recarray`.

    Parameters
    ----------
    key : str
        The column name.

    Returns
    -------
    str
        The column name that can be used in `get_table_value`.
    """
    return key.replace(',', '').replace(' ', '_').replace('.', '').replace('-', '').lower() if key else ''


def _get_single_table_value(array: numpy.recarray, col_match, col_match_with, col_val):
    return array[array[col_match] == col_match_with][col_val][0]


def get_table_value(array: numpy.recarray, col_match, col_match_with, col_val):
    """
    Get a value matched by one or more columns from a `numpy.recarray`.

    Parameters
    ----------
    array : numpy.recarray
        The array returned by the `load_lookup` function.
    col_match
        Which `column` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match_with`.
    col_match_with
        Which column `value` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match`.
    col_val: str
        The column which contains the value to look for.

    Returns
    -------
    str
        The value found or `None` if no match.
    """
    def reducer(x, values):
        col = values[1]
        value = col_match_with[values[0]]
        return x[x[col] == value]

    single = isinstance(col_match, str) and isinstance(col_match_with, str)
    try:
        value = _get_single_table_value(array, col_match, col_match_with, col_val) if single else \
            reduce(reducer, enumerate(col_match), array)[col_val][0]
        return None if _is_missing_value(value) else value
    except Exception:
        return None


def extract_grouped_data(data: str, key: str) -> str:
    """
    Extract value from a grouped data in a lookup table.

    Example:
    - with data: `Average_price_per_tonne:106950.5556;1991:-;1992:-`
    - get the value for `Average_price_per_tonne` = `106950.5556`

    Parameters
    ----------
    data
        The data to parse. Must be a string in the format `<key1>:<value>;<key2>:<value>`
    key
        The key to extract the data. If not present, `None` will be returned.

    Returns
    -------
    str
        The value found or `None` if no match.
    """
    grouped_data = reduce(lambda prev, curr: {
        **prev,
        **{curr.split(':')[0]: curr.split(':')[1]}
    }, data.split(';'), {}) if data is not None and isinstance(data, str) and len(data) > 1 else {}
    return grouped_data.get(key)


def extract_grouped_data_closest_date(data: str, year: int) -> str:
    """
    Extract date value from a grouped data in a lookup table.

    Example:
    - with data: `2000:-;2001:0.1;2002:0;2003:0;2004:0;2005:0`
    - get the value for `2001` = `0.1`

    Parameters
    ----------
    data
        The data to parse. Must be a string in the format `<key1>:<value>;<key2>:<value>`
    year
        The year to extract the data. If not present, the closest date data will be returned.

    Returns
    -------
    str
        The closest value found.
    """
    data_by_date = reduce(
        lambda prev, curr: {
            **prev,
            **{curr.split(':')[0]: curr.split(':')[1]}
        } if len(curr) > 0 and not _is_missing_value(curr.split(':')[1]) else prev,
        data.split(';'),
        {}
    ) if data is not None and isinstance(data, str) and len(data) > 1 else {}
    dist_years = list(data_by_date.keys())
    closest_year = min(dist_years, key=lambda x: abs(int(x) - year)) if len(dist_years) > 0 else None
    return None if closest_year is None else data_by_date.get(closest_year)
