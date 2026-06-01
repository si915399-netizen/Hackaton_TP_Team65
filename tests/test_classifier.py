import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.classifier import MailClassifier

SAMPLE_CONFIG = {
    "default_category": "other",
    "unreadable_category": "unreadable",
    "min_category_score": 1,
    "theme_weight": 2,
    "categories": {
        "other": {
            "folder": "other",
            "title": "Прочее",
            "priority": 0,
            "keywords": []
        },
        "unreadable": {
            "folder": "unreadable",
            "title": "Нечитаемое",
            "priority": 0,
            "keywords": []
        },
        "finance": {
            "folder": "finance",
            "title": "Финансы",
            "priority": 5,
            "keywords": ["счёт", "оплата", "бюджет"]
        },
        "hr": {
            "folder": "hr",
            "title": "HR",
            "priority": 3,
            "keywords": ["отпуск", "кадры", "найм"]
        },
        "it": {
            "folder": "it",
            "title": "IT",
            "priority": 4,
            "keywords": ["сервер", "ошибка", "доступ"]
        }
    }
}

@pytest.fixture
def classifier():
    with patch("builtins.open", mock_open(read_data=json.dumps(SAMPLE_CONFIG))):
        with patch("pathlib.Path.exists", return_value=True):
            return MailClassifier()

class TestLoadConfig:
    def test_load_config_file_not_found(self):
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                MailClassifier()

    def test_load_config_returns_dict(self, classifier):
        assert isinstance(classifier.config, dict)
        assert "categories" in classifier.config
        assert "default_category" in classifier.config

    def test_load_config_sets_attributes(self, classifier):
        assert classifier.default_category == "other"
        assert classifier.unreadable_category == "unreadable"
        assert classifier.min_category_score == 1
        assert classifier.theme_weight == 2

class TestUnreadableCategory:
    def test_none_mail_returns_unreadable(self, classifier):
        result = classifier.classify(None)
        assert result["category"] == "unreadable"

    def test_unreadable_has_zero_score(self, classifier):
        result = classifier.classify(None)
        assert result["category_score"] == 0
        assert result["matched_keywords"] == []

    def test_unreadable_folder_from_config(self, classifier):
        result = classifier.classify(None)
        assert result["folder"] == "unreadable"

class TestDefaultCategory:
    def test_no_keywords_match_returns_other(self, classifier):
        mail = {"mail_name": "test", "mail_theme": "привет", "mail_txt": "текст без ключей"}
        result = classifier.classify(mail)
        assert result["category"] == "other"

    def test_other_score_is_zero(self, classifier):
        mail = {"mail_name": "x", "mail_theme": "", "mail_txt": "xyz 123"}
        result = classifier.classify(mail)
        assert result["category_score"] == 0

    def test_score_below_min_falls_to_other(self, classifier):
        high_min_config = {**SAMPLE_CONFIG, "min_category_score": 5}
        with patch("builtins.open", mock_open(read_data=json.dumps(high_min_config))):
            with patch("pathlib.Path.exists", return_value=True):
                    clf = MailClassifier()
        mail = {"mail_name": "x", "mail_theme": "", "mail_txt": "оплата счёт"}
        result = clf.classify(mail)
        assert result["category"] == "other"

    def test_empty_mail_fields_returns_other(self, classifier):
        mail = {"mail_name": "", "mail_theme": "", "mail_txt": ""}
        result = classifier.classify(mail)
        assert result["category"] == "other"

class TestThemeWeight:
    def test_keyword_in_theme_scores_double(self, classifier):
        mail = {"mail_name": "x", "mail_theme": "счёт за услуги", "mail_txt": ""}
        result = classifier.classify(mail)
        assert result["category"] == "finance"
        assert result["category_score"] == 2
        assert result["theme_matches_count"] == 1

    def test_keyword_in_body_scores_one(self, classifier):
        mail = {"mail_name": "x", "mail_theme": "важное письмо", "mail_txt": "оплата услуг"}
        result = classifier.classify(mail)
        assert result["category"] == "finance"
        assert result["category_score"] == 1
        assert result["theme_matches_count"] == 0

    def test_theme_match_beats_body_match_of_different_category(self, classifier):
        mail = {
            "mail_name": "x",
            "mail_theme": "счёт нужно оплатизть",
            "mail_txt": "отпуск согласован"
        }
        result = classifier.classify(mail)
        assert result["category"] == "finance"

    def test_custom_theme_weight(self):
        config = {**SAMPLE_CONFIG, "theme_weight": 3}
        with patch("builtins.open", mock_open(read_data=json.dumps(config))):
            with patch("pathlib.Path.exists", return_value=True):
                    clf = MailClassifier()
        mail = {"mail_name": "x", "mail_theme": "счёт за услуги", "mail_txt": ""}
        result = clf.classify(mail)
        assert result["category_score"] == 3

class TestPriority:
    def test_higher_priority_wins_on_equal_score(self, classifier):
        mail = {
            "mail_name": "x",
            "mail_theme": "нейтральная тема",
            "mail_txt": "бюджет отпуск"
        }
        result = classifier.classify(mail)
        assert result["category"] == "finance"

    def test_lower_priority_loses_on_equal_score(self, classifier):
        mail = {
            "mail_name": "x",
            "mail_theme": "нейтральная тема",
            "mail_txt": "кадры доступ"
        }
        result = classifier.classify(mail)
        assert result["category"] == "it"

    def test_priority_in_result(self, classifier):
        mail = {"mail_name": "x", "mail_theme": "счёт", "mail_txt": ""}
        result = classifier.classify(mail)
        assert result["priority"] == 5

class TestIsBetterCategory:
    def setup_method(self):
        with patch("builtins.open", mock_open(read_data=json.dumps(SAMPLE_CONFIG))):
            with patch("pathlib.Path.exists", return_value=True):
                    self.clf = MailClassifier()

    def test_higher_score_is_better(self):
        assert self.clf.is_better_category(5, 1, 0, 3, 1, 0) is True

    def test_lower_score_is_not_better(self):
        assert self.clf.is_better_category(2, 1, 0, 5, 1, 0) is False

    def test_equal_score_more_theme_matches_is_better(self):
        assert self.clf.is_better_category(4, 3, 0, 4, 1, 0) is True

    def test_equal_score_fewer_theme_matches_is_not_better(self):
        assert self.clf.is_better_category(4, 0, 0, 4, 2, 0) is False

    def test_equal_score_equal_theme_higher_priority_is_better(self):
        assert self.clf.is_better_category(4, 2, 10, 4, 2, 3) is True

    def test_equal_score_equal_theme_equal_priority_is_not_better(self):
        assert self.clf.is_better_category(4, 2, 3, 4, 2, 3) is False

    def test_equal_score_equal_theme_lower_priority_is_not_better(self):
        assert self.clf.is_better_category(4, 2, 1, 4, 2, 5) is False

@pytest.mark.parametrize("theme,body,expected_category", [
    ("счёт к оплате", "", "finance"),
    ("", "оплата услуг", "finance"),
    ("отпуск согласован", "", "hr"),
    ("", "найм нового специалиста", "hr"),
    ("сервер недоступен", "", "it"),
    ("случайная тема", "случайный текст", "other"),
    ("", "", "other"),
])
def test_classify_parametrized(classifier, theme, body, expected_category):
    mail = {"mail_name": "test", "mail_theme": theme, "mail_txt": body}
    result = classifier.classify(mail)
    assert result["category"] == expected_category

class TestMakeResult:
    def test_result_contains_required_fields(self, classifier):
        mail = {"mail_name": "test", "mail_theme": "счёт", "mail_txt": ""}
        result = classifier.classify(mail)
        for field in ("category", "folder", "title", "priority",
                      "category_score", "theme_matches_count", "matched_keywords", "mail_name"):
            assert field in result, f"Отсутствует поле: {field}"

    def test_mail_name_preserved_in_result(self, classifier):
        mail = {"mail_name": "письмо_42", "mail_theme": "", "mail_txt": ""}
        result = classifier.classify(mail)
        assert result["mail_name"] == "письмо_42"

    def test_matched_keywords_listed(self, classifier):
        mail = {"mail_name": "x", "mail_theme": "счёт и бюджет", "mail_txt": ""}
        result = classifier.classify(mail)
        assert "счёт" in result["matched_keywords"]
        assert "бюджет" in result["matched_keywords"]

