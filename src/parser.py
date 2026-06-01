import os
from typing import Optional

# Расширения, которые гарантированно считаем текстовыми
text_types = {
    '.txt', '.eml', '.py', '.json', '.html', '.csv', '.log', '.md',
    '.xml', '.yaml', '.yml', '.cfg', '.ini'
}

MAX_FILE_SIZE = 2 * 1024 * 1024
def _is_text_file(filepath: str) -> bool:

    ext = os.path.splitext(filepath)[1].lower()
    if ext in text_types:
        return True
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
        if b'\x00' in chunk:
            return False
        chunk.decode('utf-8')
        return True
    except (UnicodeDecodeError, Exception):
        return False


def parse_file(filepath):
    if not os.path.isfile(filepath):
        return None

    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            return None
    except OSError:
        return None

    if not _is_text_file(filepath):
        return None

    try:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read(MAX_FILE_SIZE)
    except OSError:
        return None

    for enc in ('utf-8', 'windows-1251', 'latin-1'):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue

    return raw_bytes.decode('utf-8', errors='replace')
