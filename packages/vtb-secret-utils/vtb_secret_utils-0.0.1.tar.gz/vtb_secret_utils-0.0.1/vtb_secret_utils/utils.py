from typing import Optional, Any, MutableSequence, MutableMapping


def replace_placeholders_in_string(string_template: str, replace_dict: dict) -> Optional[str]:
    """
    Замена в строках placeholder'ов значениями из словаря replace_dict
    :param string_template: строка с placeholder'ами
    :param replace_dict: словарь для замены placeholder'ов
    :return: обработанная строка
    """
    if string_template is None:
        return None

    if not isinstance(string_template, str):
        raise ValueError(f"Object {string_template} isn't a string")

    for key, value in replace_dict.items():
        key = f'${key}'
        if key in string_template:
            string_template = string_template.replace(key, value)

    return string_template


def replace_placeholders(object_value: Any, replace_dict: dict) -> Optional[Any]:
    """
    Замена в строках placeholder'ов значениями из словаря replace_dict
    :param object_value: объект любого типа
    :param replace_dict: словарь для замены placeholder'ов
    :return: обработанный объект
    """
    if isinstance(object_value, MutableMapping):
        for key, value in object_value.items():
            object_value[key] = replace_placeholders(value, replace_dict)
    elif isinstance(object_value, MutableSequence):
        for idx, item in enumerate(object_value):
            object_value[idx] = replace_placeholders(item, replace_dict)
    elif isinstance(object_value, str):
        object_value = replace_placeholders_in_string(object_value, replace_dict)

    return object_value
