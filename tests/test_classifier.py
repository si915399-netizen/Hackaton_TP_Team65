import json
import pytest
from pathlib import Path
from unittest.mock import patch
from classifier import MailClassifier
from file_manager import FileManager
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if (BASE_DIR / "src").exists() and str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

@pytest.fixture
def sample_categories():
    return {
        "default_category": "other",
        "unreadable_category": "unreadable",
        "min_category_score": 1,
        "theme_weight": 2,
        "categories": {
            "spam": {
                "folder": "spam",
                "title": "Спам",
                "priority": 1,
                "keywords": ["купить", "скидка", "акция", "бесплатно"]
            },
            "critical": {
                "folder": "critical",
                "title": "Критические инциденты",
                "priority": 3,
                "keywords": ["сервер упал", "ошибка", "недоступен", "срочно"]
            },
            "support": {
                "folder": "support",
                "title": "Поддержка",
                "priority": 2,
                "keywords": ["помогите", "не работает", "проблема", "заявка"]
            },
            "other": {
                "folder": "other",
                "title": "Прочее",
                "priority": 0,
                "keywords": []
            },
            "unreadable": {
                "folder": "unreadable",
                "title": "Нечитаемые",
                "priority": 0,
                "keywords": []
            }
        }
    }


@pytest.fixture
def classifier_with_config(tmp_path, sample_categories):
    config_dir = tmp_path / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "categories.json"
    config_file.write_text(json.dumps(sample_categories, ensure_ascii=False), encoding="utf-8")

    with patch.object(MailClassifier, "__init__", lambda self: None):
        clf = MailClassifier.__new__(MailClassifier)
        clf.config_path = config_file
        clf.config = sample_categories
        clf.default_category = sample_categories["default_category"]
        clf.unreadable_category = sample_categories["unreadable_category"]
        clf.min_category_score = sample_categories["min_category_score"]
        clf.theme_weight = sample_categories["theme_weight"]
        clf.categories = sample_categories["categories"]
    return clf


@pytest.fixture
def file_manager(tmp_path):
    fm = FileManager.__new__(FileManager)
    fm.processed_dir = tmp_path / "data" / "processed"
    fm.processed_dir.mkdir(parents=True, exist_ok=True)
    return fm
