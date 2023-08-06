def convert_list_to_string(input_list: list, separator=",") -> str:
    """
    Converts a list to a string with a separator
    """
    return separator.join(input_list)


def convert_list_to_dict(input_list: list, key: str = "id") -> dict:
    """
    Converts a list to a dictionary.

    Arguments:
        :param input_list(list): The list to be converted
        :param key(str): The key of each item in list to be promoted
    """
    return {item[key]: item for item in input_list}
