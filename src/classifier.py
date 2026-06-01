import json
from pathlib import Path


class MailClassifier:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "data" / "config" / "categories.json"

        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.default_category = self.config.get("default_category", "other")
        self.unreadable_category = self.config.get("unreadable_category", "unreadable")
        self.min_category_score = self.config.get("min_category_score", self.config.get("min_matches", 1))
        self.theme_weight = self.config.get("theme_weight", 2)
        self.categories = self.config.get("categories", {})

    def load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Файл categories.json не найден: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def classify(self, cleaned_mail):
        if cleaned_mail is None:
            return self.make_result(
                category_name=self.unreadable_category,
                category_score=0,
                matched_keywords=[],
                theme_matches_count=0
            )

        mail_name = cleaned_mail.get("mail_name", "")
        theme_text = cleaned_mail.get("mail_theme", "")
        body_text = cleaned_mail.get("mail_txt", "")
        best_category = self.default_category
        best_category_score = 0
        best_theme_matches_count = 0
        best_priority = 0
        best_matched_keywords = []

        for category_name in self.categories:
            if category_name == self.default_category or category_name == self.unreadable_category:
                continue

            category_data = self.categories[category_name]
            keywords = category_data.get("keywords", [])
            priority = category_data.get("priority", 0)
            category_score = 0
            theme_matches_count = 0
            matched_keywords = []

            for keyword in keywords:
                keyword = str(keyword).strip()
                if not keyword:
                    continue
                if self.keyword_in_text(keyword, theme_text):
                    category_score += self.theme_weight
                    theme_matches_count += 1
                    matched_keywords.append(keyword)
                elif self.keyword_in_text(keyword, body_text):
                    category_score += 1
                    matched_keywords.append(keyword)

            if self.is_better_category(category_score, theme_matches_count, priority, best_category_score,
                                       best_theme_matches_count, best_priority):
                best_category = category_name
                best_category_score = category_score
                best_theme_matches_count = theme_matches_count
                best_priority = priority
                best_matched_keywords = matched_keywords

        if best_category_score < self.min_category_score:
            best_category = self.default_category
            best_category_score = 0
            best_theme_matches_count = 0
            best_matched_keywords = []

        result = self.make_result(category_name=best_category, category_score=best_category_score,
                                  matched_keywords=best_matched_keywords, theme_matches_count=best_theme_matches_count)

        result["mail_name"] = mail_name

        return result

    def keyword_in_text(self, keyword, text):
        keyword = " " + keyword.strip() + " "
        text = " " + text.strip() + " "

        return keyword in text

    def is_better_category(self, category_score, theme_matches_count, priority, best_category_score,
                           best_theme_matches_count, best_priority):
        if category_score > best_category_score:
            return True

        if category_score < best_category_score:
            return False

        if theme_matches_count > best_theme_matches_count:
            return True

        if theme_matches_count < best_theme_matches_count:
            return False

        if priority > best_priority:
            return True

        return False

    def make_result(self, category_name, category_score, matched_keywords, theme_matches_count):
        category_data = self.categories.get(category_name, {})

        return {
            "category": category_name,
            "folder": category_data.get("folder", category_name),
            "title": category_data.get("title", category_name),
            "priority": category_data.get("priority", 0),
            "category_score": category_score,
            "theme_matches_count": theme_matches_count,
            "matched_keywords": matched_keywords
        }