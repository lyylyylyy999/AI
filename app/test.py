"""调用日志解析与统计：在仓库根目录运行 python -m app.test [日志路径]。"""

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

from app.domain import InvalidMessageError, Message, summarize
from app.jsonl import parse_lines, read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(
        description="读取 JSONL 日志并打印统计；不传路径时使用内置合成样例。",
    )
    parser.add_argument("path", nargs="?", type=Path, help="UTF-8 JSONL 日志文件路径")
    args = parser.parse_args()

    messages: Iterator[Message]
    try:
        if args.path is not None:
            messages = read_jsonl(args.path)
        else:
            samples = [
                {"conversation_id": "示例会话", "role": "system", "content": "系统"},
                {"conversation_id": "示例会话", "role": "user", "content": "你好"},
                {"conversation_id": "示例会话", "role": "assistant", "content": "收到"},
            ]
            messages = parse_lines(json.dumps(item, ensure_ascii=False) for item in samples)
        statistics = summarize(messages)
    except InvalidMessageError as exc:
        print(f"日志校验失败：{exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print("读取失败：日志必须使用 UTF-8 编码。", file=sys.stderr)
        return 1
    except OSError:
        print("读取失败：请检查文件是否存在，以及是否有读取权限。", file=sys.stderr)
        return 1

    print(statistics.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
