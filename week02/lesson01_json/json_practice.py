import json
from pathlib import Path


def build_research_record() -> dict[str, object]:
    record = {
        "chinese_title": "第二周作业",
        "sample_size": 240,
        "stat_method": ["贝叶斯", "因素分析"],
        "effect_size": 0.8,
        "peer_review": True,
        "remarks": None,
        "objects": {
            "language": "chinese",
            "year": 2026,
        },
    }

    return record


def serialize_record(record: dict[str, object]) -> str:
    json_text = json.dumps(record, ensure_ascii=False, indent=2)
    return json_text


def save_record(record: dict[str, object], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def load_json(path: Path) -> object:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    record = build_research_record()
    json_text = serialize_record(record)
    path = Path("week02/lesson01_json/data/record.json")
    save_record(record, path)
    python_text = load_json(path)
    print(json_text)
    print(python_text)


if __name__ == "__main__":
    main()
