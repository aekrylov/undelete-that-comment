import pytz

MSK = pytz.timezone('Europe/Moscow')


def escape_md(text: str) -> str:
    """Escapes some special Markdown symbols"""
    return text.translate(str.maketrans({
        '_': r'\_',
        '*': r'\*',
        '`': r'\`',
        '[': r'\['
    }))
