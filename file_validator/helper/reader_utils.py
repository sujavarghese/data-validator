import re
import math
import logging
import traceback
from datetime import datetime
import numpy as np

logger = logging.getLogger()

FLOAT_RE = re.compile('^[-+]?[0-9]*\.?[0-9]+$')
FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def is_empty(val):
    return (val is np.nan) or (val is None) or (val is "")


def to_snake(non_snake_str):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', non_snake_str)
    return ALL_CAP_RE.sub(r'\1_\2', s1).lower()


def to_int(val, default=None):
    """
    Cast value to integer.

    :Parameters:
    val: raw value
    default: default value if error in converting
    """
    int_val = default

    try:
        int_val = int(val)
    except ValueError:
        if FLOAT_RE.match(val):
            int_val = int(float(val))
    except TypeError as e:
        # logger.warning(e)
        pass

    return int_val


def to_str(val, default=None):
    """
    Cast value to string.

    :Parameters:
    val: raw value
    default: default value if error in converting
    """
    str_val = default

    try:
        if not is_empty(val):
            str_val = str(val)
    except Exception as e:
        # logger.warning(e)
        # traceback.print_exc()
        pass

    return str_val


def to_float(val, default=None):
    """
    Cast value to float.

    :Parameters:
    val: raw value
    default: default value if error in converting
    """
    float_val = default

    try:
        if not is_empty(val):
            float_val = float(val)
    except Exception as e:
        # logger.warning(e)
        # traceback.print_exc()
        pass
    return float_val


def dollar_str_to_float(val, default=None):
    try:
        # Remove `$` & `,`
        float_str = re.sub(r'[\$,]', '', val)

        # If negative: Remove `(` & `)` & Prepend `-`
        if re.match(r'\(\d+\.\d+\)', float_str):
            float_str = re.sub(r'[\(\)]', '', float_str)
            float_str = '-{}'.format(float_str)

        float_val = float(float_str)
    except AttributeError:
        traceback.print_exc()
        float_val = float(val)
    except Exception as e:
        # logger.warning(e)
        # traceback.print_exc()
        float_val = None

    return float_val


def str_to_datetime(str_val, format='%d/%m/%Y'):
    return datetime.strptime(str_val, format) if not is_empty(str_val) else None


def datetime_to_str(datetime_str, format='%d/%m/%Y %I:%M:%S %p'):
    dt = str_to_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S.%f')
    return dt.strftime(format) if dt else None


def ts_unix_to_iso(ts, default=None):
    """
    Convert unix timestamp to native DateTime
    :param ts:
    :return:
    """
    iso_ts = default

    if not is_empty(ts):
        try:
            int_ts = int(ts)
            iso_ts = datetime.utcfromtimestamp(int_ts).isoformat()
        except Exception as e:
            # logger.warning(e)
            pass

    return iso_ts


def round_down(val):
    """
    Round down value using the floor function.

    :Parameters:
    val: raw float value
    """
    floor_val = val

    try:
        if not is_empty(val):
            float_val = float(val)
            floor_val = math.floor(float_val)
    except Exception as e:
        # logger.warning(e)
        pass

    return floor_val


def set_bool(val, true_val=[1, '1']):
    bool_val = False
    if (type(true_val) == list and val in true_val) or (val == true_val):
        bool_val = True
    return bool_val


def concat(values, sep=', '):
    """
    Concat list of values using sep to return a single string.

    args:
        values: List of values
        sep: String value to concat the values
    """
    concat_str = None
    try:
        concat_str = sep.join([str(v) for v in values if not is_empty(v)])
    except Exception as e:
        logger.warning(e)
        pass
    return concat_str


def normalise(str_val, casing='lower'):
    """
    Normalise a string value by cleaning up spaces.
    With options to convert to a single casing. Default to lowercase.

    :args:
    str_val: String value
    casing: lower or upper or None
    """
    norm_val = None
    try:
        clean_val = clean(str_val)
        if casing == 'lower':
            norm_val = clean_val.lower()
        elif casing == 'upper':
            norm_val = clean_val.upper()
        else:
            norm_val = clean_val
    except Exception as e:
        # logger.warning(e)
        pass
    return norm_val


def clean(val):
    """Merge multiple spaces to single space. Remove trailing/leading spaces.

    :Args:
    val: string value to clean

    :Returns:
    cleaned value
    """

    val = re.sub(r'/s+', r'/s', val)
    return val.strip()


def clean_column_names(df):
    """Clean column names using :func:etl.utils.clean

    :Args:
    df: Pandas dataframe object

    :Returns:
    Renamed dataframe with clean column names
    """

    clean_names = {n: clean(n) for n in df.columns}
    return df.rename(columns=clean_names)
