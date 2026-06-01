import json
from pathlib import Path
from graph_cluster import cluster_keywords_by_cooccurrence

BASE_DIR = Path(__file__).resolve().parent
CANDIDATES_FILE = BASE_DIR / "data" / "config" / "candidate_keywords.json"
OUTPUT_CATEGORIES = BASE_DIR / "data" / "config" / "categories.json"

def build_categories():
    if not CANDIDATES_FILE.exists():
        print("Сначала запустите создание кандидатов.")
        return
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)
    words = candidates.get("words", [])
    phrases = candidates.get("phrases", [])
    all_candidates = words + phrases
    if not all_candidates:
        print("Нет кандидатов.")
        return
    clustered = cluster_keywords_by_cooccurrence(all_candidates, min_cooccurrence=2, top_n=150)
    old_config = {}
    if OUTPUT_CATEGORIES.exists():
        with open(OUTPUT_CATEGORIES, "r", encoding="utf-8") as f:
            old_config = json.load(f)
    new_categories = {}
    for cat in clustered:
        cat_name = cat["name"]
        new_categories[cat_name] = {
            "keywords": cat["keywords"],
            "priority": 0,
            "folder": cat_name,
            "title": cat_name
        }
    default_settings = {
        "default_category": old_config.get("default_category", "other"),
        "unreadable_category": old_config.get("unreadable_category", "unreadable"),
        "min_category_score": old_config.get("min_category_score", 1),
        "theme_weight": old_config.get("theme_weight", 2),
        "categories": new_categories
    }
    with open(OUTPUT_CATEGORIES, "w", encoding="utf-8") as f:
        json.dump(default_settings, f, ensure_ascii=False, indent=4)
    print(f"Сохранено {len(new_categories)} категорий в {OUTPUT_CATEGORIES}")

if __name__ == "__main__":
    build_categories()