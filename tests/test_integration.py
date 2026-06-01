from pathlib import Path
from src.parser import parse_file
from src.cleaner import process_raw_email

class TestIntegration:

    def test_full_pipeline_spam(self, tmp_path, classifier_with_config):
        f = tmp_path / "promo.txt"
        f.write_text(
            "Subject: Rasprodazha slonov!\n\nAkcija besplatno tolko segodnja geekbrains skidki dlya vas",
            encoding="utf-8"
        )
        raw = parse_file(str(f))
        assert raw is not None
        cleaned = process_raw_email(raw, f.name)
        result = classifier_with_config.classify(cleaned)
        assert result["category"] == "spam"

    def test_full_pipeline_unreadable_file(self, tmp_path, classifier_with_config):
        bad_file = tmp_path / "corrupt_data_dump.dat"
        bad_file.write_bytes(b"\x00\xff\xfe\xfd")
        raw = parse_file(str(bad_file))
        res = classifier_with_config.classify(raw)
        assert res["category"] == "unreadable"

    def test_full_pipeline_unknown_category(self, tmp_path, classifier_with_config):
        f = tmp_path / "random_stuff.txt"
        f.write_text(
            "Subject: Nu privet\n\nKak dela? Vse normalno vrode.",
            encoding="utf-8"
        )
        raw = parse_file(str(f))
        cleaned = process_raw_email(raw, f.name)
        out = classifier_with_config.classify(cleaned)
        assert out["category"] == "other"
