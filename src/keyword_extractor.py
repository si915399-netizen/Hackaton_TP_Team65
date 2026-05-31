import json
from pathlib import Path


class KeywordExtractor:
    def __init__(self, min_word_length=4, min_total_count=2, min_mail_count=2, max_mail_part=0.8):
        self.min_word_length = min_word_length
        self.min_total_count = min_total_count
        self.min_mail_count = min_mail_count
        self.max_mail_part = max_mail_part

    def extract_keywords(self, cleaned_mails):
        word_stats = {}
        phrase_stats = {}
        total_mails = len(cleaned_mails)

        for mail in cleaned_mails:
            file_name = mail.get("file_name", "")
            text = mail.get("text", "")
            words = self.get_words_from_text(text)
            phrases = self.get_phrases_from_words(words)
            self.add_items_to_stats(words, file_name, word_stats)
            self.add_items_to_stats(phrases, file_name, phrase_stats)

        words_result = self.prepare_result(word_stats, total_mails)
        phrases_result = self.prepare_result(phrase_stats, total_mails)

        return {
            "words": words_result,
            "phrases": phrases_result
        }

    def get_words_from_text(self, text):
        all_words = text.split()
        correct_words = []

        for word in all_words:
            if len(word) < self.min_word_length:
                continue
            if word.isdigit():
                continue
            correct_words.append(word)

        return correct_words

    def get_phrases_from_words(self, words):
        phrases = []

        for i in range(len(words) - 1):
            phrase = words[i] + " " + words[i + 1]
            phrases.append(phrase)

        for i in range(len(words) - 2):
            phrase = words[i] + " " + words[i + 1] + " " + words[i + 2]
            phrases.append(phrase)

        return phrases

    def add_items_to_stats(self, items, file_name, statistics):
        for item in items:
            if item not in statistics:
                statistics[item] = {
                    "total_count": 0,
                    "files": set()
                }
            statistics[item]["total_count"] += 1
            statistics[item]["files"].add(file_name)

    def prepare_result(self, statistics, total_mails):
        result = []

        for keyword in statistics:
            total_count = statistics[keyword]["total_count"]
            files = statistics[keyword]["files"]
            mail_count = len(files)
            if total_count < self.min_total_count:
                continue
            if mail_count < self.min_mail_count:
                continue
            mail_part = mail_count / total_mails
            if mail_part > self.max_mail_part:
                continue
            score = total_count + mail_count * 2
            result.append({
                "keyword": keyword,
                "total_count": total_count,
                "mail_count": mail_count,
                "score": score,
                "examples": sorted(list(files))[:10]
            })

        result.sort(key=lambda item: item["score"], reverse=True)

        return result


def save_keywords_to_json(result):
    file_path = Path("data/config/candidate_keywords.json")

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)