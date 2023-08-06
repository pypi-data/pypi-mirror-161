import inspect

COLORS = {
    'red': (188, 63, 60),
    'yellow': (187, 181, 41),
    'orange': (204, 120, 50),
    'blue': (40, 123, 22),
    'green': (106, 135, 89),
    'cyan': (104, 151, 187),
    'purple': (152, 118, 170),
    'brown': (138, 101, 59),
    'error': (255, 107, 104),
    'gray': (85, 85, 85),
    'white': (187, 187, 187)
}


def _foreground(r=None, g=None, b=None):
    if r or g or b:
        r = r or 0
        g = g or 0
        b = b or 0
        return f"38;2;{r};{g};{b}"
    return None


def _background(r=None, g=None, b=None):
    if r or g or b:
        r = r or 0
        g = g or 0
        b = b or 0
        return f"48;2;{r};{g};{b}"
    return None


def _decor(decoration):
    if not decoration:
        return None
    elif 'bold' in decoration:
        return '1'
    elif 'italicize' in decoration:
        return '3'
    elif 'underline' in decoration:
        return '4'
    else:
        return None


def colorize(message, color=None, bg=None, decoration=None):
    color = color and _foreground(*COLORS[color]) or None
    bg = bg and _background(*COLORS[bg]) or None
    decoration = _decor(decoration)
    valid_escapes = [e for e in [decoration, color, bg] if e]
    if valid_escapes:
        escapes = ';'.join(valid_escapes)
        return f'\033[{escapes}m{message}\033[0m'
    return str(message)


def error(*messages, title='ERR'):
    title = colorize("{:^10}".format(title), color='white', bg='red', decoration='bold')
    message_str = ', '.join([str(m) for m in messages])
    message = colorize(message_str, color='error')
    print(f"{title}\t{message}")
    return message_str


def success(*messages):
    title = colorize("{:^10}".format("DONE"), color='white', bg='green', decoration='bold')
    message_str = ', '.join([str(m) for m in messages])
    message = colorize(message_str, color='green')
    print(f"{title}\t{message}")
    return message_str


def log(message):
    title = colorize("{:^10}".format("LOG"), color='white', bg='gray')
    print(f"{title}\t{message}")
    return message


def condition(cond=None, expr=None, result=False):
    title = colorize("{:^10}".format("COND"), color='white', bg='purple')
    result = colorize(result, color='orange')
    expr = colorize(expr, color='cyan')
    arrow = ": -> "
    if cond:
        cond = colorize(cond, color='purple', decoration='bold')
        l_paren = colorize(" (", color='purple', decoration='bold')
        r_paren = colorize(")", color='purple', decoration='bold')
        print(f"{title}\t{cond}{l_paren}{expr}{r_paren}{arrow}{result}")
        return f"{cond}{l_paren}{expr}{r_paren}{arrow}{result}"
    print(f"{title}\t{expr}{arrow}{result}")
    return f"{expr}{arrow}{result}"


def data(name=None, value=None, tabs=1):
    title = colorize("{:^10}".format(f"{name or 'DATA'}"), color='white', bg='cyan', decoration='bold')
    print(f"{title}\n" + "\t" * (tabs - 1) + f"{_colored_value(value, tabs=tabs)}")
    return str(value)


def _can_be_dict(value):
    from_class = inspect.isclass(value) and hasattr(value, 'keys') and hasattr(value, '__getitem__')
    from_dict = type(value) == dict
    return from_dict or from_class


def _colored_dict(value, tabs=1):
    result = "{\n"
    for k, v in value.items():
        result += "\t" * tabs + colorize(k, color='cyan') + ": "
        if _can_be_dict(v):
            result += _colored_dict(dict(v), tabs=tabs + 1)
        else:
            result += "" * tabs + f"{v},\n"
    return result + "\t" * (tabs - 1) + "}\n"


def _colored_value(value, tabs=1):
    if _can_be_dict(value):
        return _colored_dict(value, tabs=tabs)
    return f"{value}"


if __name__ == "__main__":
    mydict = {'one': 1, 'two': {'three': 3, 'four': 4, }}
    print(error("ERROR", 'error with syntax', mydict))
    print(success("Data is valid", mydict))
    print(condition("if", 'type(mydict) == dict', type(mydict) == dict))
    print(log("checking data"))
    print(data("mydict", mydict))
