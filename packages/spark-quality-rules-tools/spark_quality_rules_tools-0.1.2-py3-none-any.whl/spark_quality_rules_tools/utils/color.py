from color_tools import colored


def get_color(text):
    text = colored(f'{text}', 'green')
    return text


def get_color_b(text):
    text = colored(f'{text}', 'blue', attrs=['bold'])
    return text
