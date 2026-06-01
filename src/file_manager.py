import shutil
from pathlib import Path


class FileManager:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        processed_dir = base_dir / "data" / "processed"
        self.processed_dir = Path(processed_dir)

    def move_file_to_category(self, source_file_path, classification_result):
        source_file_path = Path(source_file_path)

        if not source_file_path.exists():
            return {
                "success": False,
                "source_file": str(source_file_path),
                "target_file": "",
                "message": "Исходный файл не найден"
            }

        folder_name = classification_result.get("folder", "other")
        category_dir = self.processed_dir / folder_name
        category_dir.mkdir(parents=True, exist_ok=True)
        target_file_path = category_dir / source_file_path.name

        try:
            shutil.move(str(source_file_path), str(target_file_path))
            return {
                "success": True,
                "source_file": str(source_file_path),
                "target_file": str(target_file_path),
                "category": classification_result.get("category", "other"),
                "folder": folder_name,
                "message": "Файл успешно перемещён"
            }
        except OSError as error:
            return {
                "success": False,
                "source_file": str(source_file_path),
                "target_file": str(target_file_path),
                "category": classification_result.get("category", "other"),
                "folder": folder_name,
                "message": f"Ошибка при перемещении файла: {error}"
            }

    def create_category_folders(self, categories):
        for category_name in categories:
            category_data = categories[category_name]
            folder_name = category_data.get("folder", category_name)
            category_dir = self.processed_dir / folder_name
            category_dir.mkdir(parents=True, exist_ok=True)