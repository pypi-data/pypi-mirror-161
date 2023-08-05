import re


def first_lower(s):
    """
    Convert first letter of a string to lowercase
    :param s: String to make Lowercase
    :return: String with first letter lowercase
    """
    if len(s) == 0:
        return s
    return s[0].lower() + s[1:]


def to_camel_case(snake_str):
    """
    Convert snake_case to UpperCamelCase
    :param snake_str:
    :return: string in upper camel case
    """
    # We capitalize the first letter of each component
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in snake_str.split('_'))


def to_lower_camel_case(snake_str):
    """
    Convert snake_case to lowerCamelCase
    :param snake_str:
    :return: string in lower camel case
    """
    return first_lower(to_camel_case(snake_str))


# see https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
to_snake_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')


def to_snake_case(camel_str):
    """
    Convert UpperCamelCase or camelCase to snake_case
    :param camel_str:
    :return: string in snake case
    """
    return to_snake_case_pattern.sub('_', camel_str).lower()
