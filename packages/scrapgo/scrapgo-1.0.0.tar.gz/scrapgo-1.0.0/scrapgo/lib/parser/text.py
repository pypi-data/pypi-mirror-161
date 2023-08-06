def parse_number(value:str):
    if isinstance(value, (int, float)):
        return value

    value = value.strip('.')
    dot_count = value.count('.')

    if dot_count == 0:
        tokens = filter(str.isdigit, value)
        return int(''.join(tokens))
    elif dot_count == 1:
        tokens = filter(lambda c: c == '.' or c.isdigit(), value)
        return float(''.join(tokens))
    else:
        return value