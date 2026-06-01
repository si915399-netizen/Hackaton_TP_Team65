import re
import sys
from pathlib import Path

def load_stopwords(filepath=None):
    if filepath is None:
        base_dir = Path(__file__).resolve().parent
        filepath = ( base_dir.parent / "data" / "stopwords.txt")
    stopwords = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if not word:
                    continue
                if word.startswith("#"):
                    continue
                stopwords.add(word)
    except FileNotFoundError:
        print(
            f"[WARNING] Stopwords file not found: {filepath}",
            file=sys.stderr
        )
    return stopwords

rubbish = load_stopwords()
t_words = {
    "vpn",
    "sql",
    "api",
    "http",
    "https",
    "ftp",
    "ssh",
    "dns",
    "tcp",
    "udp",
    "ip",
    "smtp",
    "imap",
    "pop3",
    "json",
    "xml",
    "csv",
    "html",
    "css",
    "javascript",
    "python",
    "java",
    "linux",
    "windows",
    "server",
    "database",
}

TRANSLIT_TABLE = {
    'shch': 'щ', 'Shch': 'Щ', 'SHCH': 'Щ',
    'shh': 'щ', 'Shh': 'Щ', 'SHH': 'Щ', 'yoh': 'ё', 'Yoh': 'Ё', 'YOH': 'Ё',
    'zh': 'ж', 'Zh': 'Ж', 'ZH': 'Ж','ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
    'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш','eh': 'э', 'Eh': 'Э', 'EH': 'Э','yu': 'ю', 'Yu': 'Ю', 'YU': 'Ю',
    'ya': 'я', 'Ya': 'Я', 'YA': 'Я','yo': 'ё', 'Yo': 'Ё', 'YO': 'Ё','je': 'е', 'Je': 'Е', 'JE': 'Е',
    'ye': 'е', 'Ye': 'Е', 'YE': 'Е','kh': 'х', 'Kh': 'Х', 'KH': 'Х', 'ts': 'ц', 'Ts': 'Ц', 'TS': 'Ц',
    'a': 'а', 'b': 'б', 'c': 'ц', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х', 'i': 'и',
    'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
    'p': 'п', 'q': 'к', 'r': 'р','s': 'с', 't': 'т', 'u': 'у',
    'v': 'в', 'w': 'в', 'x': 'кс','y': 'ы', 'z': 'з',
    'A': 'А', 'B': 'Б', 'C': 'Ц','D': 'Д', 'E': 'Е', 'F': 'Ф',
    'G': 'Г', 'H': 'Х', 'I': 'И','J': 'Й', 'K': 'К', 'L': 'Л',
    'M': 'М', 'N': 'Н', 'O': 'О','P': 'П', 'Q': 'К', 'R': 'Р',
    'S': 'С', 'T': 'Т', 'U': 'У','V': 'В', 'W': 'В', 'X': 'Кс','Y': 'Ы', 'Z': 'З',
}
_translit_pattern = re.compile("|".join(re.escape(k)for k in sorted(TRANSLIT_TABLE.keys(), key=len,reverse=True )))
def _translit_replace(match):
    return TRANSLIT_TABLE.get( match.group(0), match.group(0) )

def translit_to_cyrillic(text):
    if not text:
        return ""
    words = text.split()
    converted = []
    for word in words:
        if word.lower() in t_words:
            converted.append(word)
            continue
        if re.search(r"[а-яё]", word, re.IGNORECASE):
            converted.append(word)
            continue
        converted.append(_translit_pattern.sub( _translit_replace, word))
    return " ".join(converted)

def clean_text(text, remove_stopwords=True):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|ftp://\S+|www\.\S+','', text)
    text = re.sub(r'\S+@\S+','', text)
    text = re.sub(r'[^a-zа-яё0-9\s]',' ', text )
    text = (text.replace('-', ' ').replace('_', ' ').replace('–', ' ') .replace('—', ' ') )
    text = re.sub(r'\s+',' ', text  ).strip()
    if remove_stopwords:
        words = text.split()
        words = [
            word
            for word in words
            if word not in rubbish
            and len(word) > 1
        ]
        text = " ".join(words)
    return text

head_patterns = [
    ('from', re.compile(r'^from\s*:\s*(.+)$', re.I)),
    ('to', re.compile(r'^to\s*:\s*(.+)$', re.I)),
    ('subject', re.compile(r'^subject\s*:\s*(.+)$', re.I)),
    ('date', re.compile(r'^date\s*:\s*(.+)$', re.I)),
    ('from', re.compile(r'^sender\s*:\s*(.+)$', re.I)),
    ('reply_to', re.compile(r'^reply-to\s*:\s*(.+)$', re.I)),
    ('from', re.compile(r'^от кого\s*:\s*(.+)$', re.I)),
    ('from', re.compile(r'^от\s*:\s*(.+)$', re.I)),
    ('to', re.compile(r'^кому\s*:\s*(.+)$', re.I)),
    ('subject', re.compile(r'^тема\s*:\s*(.+)$', re.I)),
    ('date', re.compile(r'^дата\s*:\s*(.+)$', re.I)),
]

def _extract_fields(raw):
    fields = {'from': '','to': '','subject': '','date': '','body': raw}
    lines = raw.splitlines()
    header_end = 0
    for i, line in enumerate(lines[:50]):
        line_stripped = line.strip()
        if not line_stripped:
            header_end = i + 1
            break
        matched = False
        for name, pattern in head_patterns:
            match = pattern.match(line_stripped)
            if match:
                if name in fields and not fields[name]:
                    fields[name] = match.group(1).strip()
                matched = True
                header_end = i + 1
                break
        if not matched:
            header_end = i
            break
    if header_end < len(lines):
        fields['body'] = (
            "\n".join(lines[header_end:])
            .strip()
        )
    return fields

def process_raw_email(raw_text, filename):
    fields = _extract_fields(raw_text)
    subject_raw = clean_text(
        fields["subject"],
        remove_stopwords=False
    )
    body_raw = clean_text(
        fields["body"],
        remove_stopwords=True
    )
    return {
        "mail_name": filename,
        "mail_theme": translit_to_cyrillic(subject_raw),
        "mail_txt": translit_to_cyrillic(body_raw),
        "from": translit_to_cyrillic(fields["from"]),
        "to": translit_to_cyrillic(fields["to"]),
        "subject": translit_to_cyrillic(subject_raw),
        "date": fields["date"],
    }

def prepare_text_for_classification(raw_text, filename):
    data = process_raw_email( raw_text,filename)
    theme = data["mail_theme"]
    body = data["mail_txt"]
    return f"{theme} {theme} {body}"
