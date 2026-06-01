import pytest
from pathlib import Path
from src.parser import parse_file, _is_text_file

class TestParser:

    def test_read_plain_text_file(self, tmp_path):
        f = tmp_path / "mail.txt"
        f.write_text("Subject: Check\n\nРебят, тут такое дело, надо потестить парсер срочно", encoding="utf-8")
        result = parse_file(str(f))
        assert result is not None
        assert "потестить" in result

    def test_read_eml_file(self, tmp_path):
        f = tmp_path / "mail.eml"
        f.write_text("From: ivan_vse_propalo@corp.ru\nSubject: Help\n\nБаза лежит, ничего не работает!!", encoding="utf-8")
        result = parse_file(str(f))
        assert result is not None
        assert "База лежит" in result

    def test_nonexistent_file_returns_none(self, tmp_path):
        res = parse_file(str(tmp_path / "ghost_file_123.txt"))
        assert None is res

    def test_binary_file_returns_none(self, tmp_path):
        f = tmp_path / "file.bin"
        f.write_bytes(b"\x00\x01\x02\x03\xff\xfe")
        out = parse_file(str(f))
        assert out is None

    def test_oversized_file_returns_none(self, tmp_path):
        f = tmp_path / "big_dump.txt"
        with open(f, "wb") as out:
            out.write(b"x" * (2 * 1024 * 1024 + 500))
        result = parse_file(str(f))
        assert result is None

    def test_empty_file_returns_empty_string(self, tmp_path):
        f = tmp_path / "empty_item.txt"
        f.write_text("", encoding="utf-8")
        res = parse_file(str(f))
        assert res is not None
        assert res == ""

    def test_windows1251_encoding(self, tmp_path):
        f = tmp_path / "cp1251.txt"
        f.write_bytes("Важное уведомление".encode("windows-1251"))
        result = parse_file(str(f))
        assert "Важное уведомление" in result
