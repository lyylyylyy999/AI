import json
from pathlib import Path

DEFALUT_PATH = Path(__file__).resolve().parent / "data"

def build_research_record() -> dict[str, object]:
    record = {
        "chinese_title": "第二周作业",
        "sample_size": 240,
        "statistical_methods": ["贝叶斯", "因素分析"],
        "effect_size": 0.8,
        "peer_reviewed": True,
        "remarks": None,
        "metadata": {
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


def main(tmp_path: Path) -> None:
    record = build_research_record()
    json_text = serialize_record(record)
    record_path = tmp_path / "record.json"
    save_record(record, record_path)
    python_text = load_json(record_path)
    print(json_text)
    print(python_text)


if __name__ == "__main__":
    main(tmp_path=DEFALUT_PATH)
