import pytest
from src.keyword_extractor import KeywordExtractor

class Test_Keyword_Extractor:

    @pytest.fixture
    def extractor(self):
        return KeywordExtractor(
            min_word_length=3,
            min_total_count=2,
            min_mail_count=2,
            max_mail_part=1.0,
            theme_weight=3
        )

    def test_extracts_frequent_words(self, extractor):
        dataset = [
            {"mail_name": "1.txt", "mail_theme": "ошибка сервера", "mail_txt": "сервер недоступен"},
            {"mail_name": "2.txt", "mail_theme": "ошибка базы", "mail_txt": "база недоступна"},
        ]
        res = extractor.extract_keywords(dataset)
        words = [w["keyword"] for w in res["words"]]
        assert "ошибка" in words

    def test_single_mail_word_excluded(self, extractor):
        items = [
            {"mail_name": "a.txt", "mail_theme": "уникальное слово", "mail_txt": ""},
            {"mail_name": "b.txt", "mail_theme": "другое", "mail_txt": ""},
        ]
        out = extractor.extract_keywords(items)
        words = [w["keyword"] for w in out["words"]]
        assert "уникальное" not in words

    def test_empty_mails_list(self, extractor):
        result = extractor.extract_keywords([])
        assert result["words"] == []
        assert result["phrases"] == []

    def test_result_sorted_by_score(self, extractor):
        mails_list = [
            {"mail_name": f"m_{i}.txt", "mail_theme": "сервер ошибка проблема", "mail_txt": "сервер"}
            for i in range(3)
        ]
        res = extractor.extract_keywords(mails_list)
        scores = [item["score"] for item in res["words"]]
        assert scores == sorted(scores, reverse=True)

    def test_get_phrases_from_words(self, extractor):
        arr = ["один", "два", "три", "четыре"]
        phrases = extractor.get_phrases_from_words(arr)
        assert "один два" in phrases
        assert "один два три" in phrases
