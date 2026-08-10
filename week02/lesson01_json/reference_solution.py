"""W2-01 本地 JSON 往返参考实现。"""

import json
from pathlib import Path

ResearchRecord = dict[str, object]


def build_research_record() -> ResearchRecord:
    """创建包含常见 JSON 值类型的研究记录。"""
    return {
        "title": "睡眠时长与研究生压力水平",
        "sample_size": 240,
        "statistical_methods": ["线性回归", "Bootstrap"],
        "effect_size": 0.31,
        "peer_reviewed": True,
        "notes": None,
        "metadata": {"language": "zh-CN", "year": 2026},
    }


def serialize_record(record: ResearchRecord) -> str:
    """把 Python 研究记录序列化为便于阅读的 JSON 字符串。"""
    return json.dumps(record, ensure_ascii=False, indent=2)


def save_record(record: ResearchRecord, path: Path) -> None:
    """把研究记录写入 UTF-8 JSON 文件。"""
    with path.open("w", encoding="utf-8") as file:
        json.dump(record, file, ensure_ascii=False, indent=2)


def load_json(path: Path) -> object:
    """读取 JSON 文件；返回值尚未经过业务契约校验。"""
    with path.open("r", encoding="utf-8") as file:
        loaded: object = json.load(file)
    return loaded
