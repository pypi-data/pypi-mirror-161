def dict_to_list(dict_object: dict) -> list[dict]:
    new_list = list()
    for k, v in dict_object.items():
        new_list.append({k: v})
    return new_list
