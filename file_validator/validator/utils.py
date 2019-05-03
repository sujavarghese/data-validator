from datetime import datetime


def empty(value):
    if isinstance(value, str):
        value = value.strip()

    if value:
        return False
    return True


def required(value):
    return not empty(value)


def is_date(value, formats=[]):
    if not formats:
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
        ]
    for format_str in formats:
        try:
            datetime.strptime(value, format_str)
            is_valid_date = True
            break
        except ValueError:
            is_valid_date = False

    return is_valid_date


def upper_case(value):
    return str(value).upper()


def lower_case(value):
    return str(value).lower()
