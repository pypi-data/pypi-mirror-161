from numbers import Number

STRING_FLOAT_FORMAT = '{:.5g}'


def parse_to_vector(text):
    """
    Return real vector from comma separated text.
    """
    try:
        values = [float(value) for value in text.split(',')]
    except ValueError:
        values = []
    return values


def display_as_vector(values, number_format=STRING_FLOAT_FORMAT):
    """
    Display real vector values in a widget. Also handle scalar
    """
    if isinstance(values, Number):
        new_text = STRING_FLOAT_FORMAT.format(values)
    else:
        new_text = ", ".join(number_format.format(value) for value in values)

    return new_text


def display_as_integer_vector(values):
    """
    Display real vector values in a widget. Also handle scalar
    """
    if isinstance(values, Number):
        new_text = f"{values}"
    else:
        new_text = ", ".join(str(value) for value in values)

    return new_text


def parse_to_integer_vector(text):
    """
    Return integer vector from comma separated text.
    """
    try:
        values = [int(value) for value in text.split(',')]
    except ValueError:
        values = []

    return values


def parse_to_integer(text):
    try:
        value = int(text)
    except ValueError:
        value = None

    return value


def display_as_integer(value):
    return f"{value}"
