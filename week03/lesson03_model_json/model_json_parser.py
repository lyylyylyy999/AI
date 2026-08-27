import json

from week02.lesson02_validation.research_schema import (
    ResearchSummary,
    validate_research_summary,
)


def parse_research_summary_content(content: str) -> ResearchSummary:
    data = content.strip()
    if data == "":
        raise ValueError("content 不能为空")
    lines = data.splitlines()
    first_line = lines[0].strip()
    last_line = lines[-1].strip()
    if (first_line == "```json" or first_line == "```") and last_line == "```":
        data = "\n".join(lines[1:-1]).strip()
        if data == "":
            raise ValueError("content 不能为空")
    try:
        parsed_data: object = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("content 不是合法的 JSON")
    result = validate_research_summary(parsed_data)
    return result
