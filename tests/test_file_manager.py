from pathlib import Path

class TestFileManager:

    def test_move_file_success(self, file_manager, tmp_path):
        src = tmp_path / "test_mail.txt"
        src.write_text("content")
        res = file_manager.move_file_to_category(src, {"folder": "spam", "category": "spam"})
        assert res["success"] is True
        assert not src.exists()
        assert (file_manager.processed_dir / "spam" / "test_mail.txt").exists()

    def test_move_nonexistent_file(self, file_manager, tmp_path):
        out = file_manager.move_file_to_category(
            tmp_path / "absent_file.txt", {"folder": "other", "category": "other"}
        )
        assert out["success"] is False

    def test_move_creates_category_folder(self, file_manager, tmp_path):
        source_file = tmp_path / "message.txt"
        source_file.write_text("hi")
        file_manager.move_file_to_category(source_file, {"folder": "custom_dir", "category": "custom_dir"})
        assert (file_manager.processed_dir / "custom_dir").exists()

    def test_create_category_folders(self, file_manager):
        cfg = {
            "spam": {"folder": "spam"},
            "critical": {"folder": "critical"},
        }
        file_manager.create_category_folders(cfg)
        assert (file_manager.processed_dir / "spam").exists()
        assert (file_manager.processed_dir / "critical").exists()
