from pathlib import Path
from parser import parse_file
from cleaner import process_raw_email
from keyword_extractor import KeywordExtractor, save_keywords_to_json


BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "data" / "inbox"


def prepare_cleaned_mails():
    cleaned_mails = []
    skipped_files = []

    if not INBOX_DIR.exists():
        print(f"Папка с письмами не найдена: {INBOX_DIR}")
        return cleaned_mails, skipped_files

    for file_path in sorted(INBOX_DIR.iterdir()):
        if not file_path.is_file():
            continue
        raw_text = parse_file(str(file_path))
        if raw_text is None:
            skipped_files.append(file_path.name)
            continue
        cleaned_mail = process_raw_email(raw_text, file_path.name)
        cleaned_mails.append(cleaned_mail)

    return cleaned_mails, skipped_files


def create_candidates_keywords():
    cleaned_mails, skipped_files = prepare_cleaned_mails()

    if not cleaned_mails:
        print("Нет писем для анализа.")
        return

    extractor = KeywordExtractor(min_word_length=4, min_total_count=2, min_mail_count=2, max_mail_part=0.8,
                                 theme_weight=3)

    result = extractor.extract_keywords(cleaned_mails)
    result["skipped_files"] = skipped_files
    save_keywords_to_json(result)
    build_categories()
    print("Файл candidates_keywords.json создан.")
    print(f"Обработано писем: {len(cleaned_mails)}")
    print(f"Пропущено файлов: {len(skipped_files)}")


if __name__ == "__main__":
    create_candidates_keywords()
