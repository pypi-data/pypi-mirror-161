def parse_bool_string(input_: str, default: bool) -> bool:
    """Cast input value to its logical boolean value if possible
    or return default value if it's not.
    :param input_: input value
    :param default: default return value
    :return: logical boolean value on an input
    """
    if input_ in ("True", "true", 1, "1"):
        return True
    if input_ in ("False", "false", 0, "0"):
        return False
    return default